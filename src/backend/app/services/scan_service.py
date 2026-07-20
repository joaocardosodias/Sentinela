import uuid
from app.entities.scan_entity import ScanPlaca, ScanStatusValidacao, Scan
from app.models.scan_model import ScanModel


class ScanService:

    @staticmethod
    def _parse_placa(raw: str) -> ScanPlaca:
        """Valida a placa lida pelo drone: mínimo 7 caracteres, normalizada para maiúsculas."""
        if not raw or len(raw.strip()) < 7:
            raise ValueError("Placa inválida. Deve ter ao menos 7 caracteres.")
        return ScanPlaca(raw.strip().upper())

    @staticmethod
    def _parse_status(raw: str) -> ScanStatusValidacao:
        """Valida se o status de validação está entre os valores permitidos."""
        if not raw or raw not in ScanStatusValidacao.VALID:
            raise ValueError(f"Status inválido. Use: {', '.join(ScanStatusValidacao.VALID)}")
        return ScanStatusValidacao(raw)

    @staticmethod
    def get_all(page=1, per_page=20, status=None, match=None, drone_id=None) -> tuple:
        """Retorna lista paginada de scans com filtros opcionais."""
        return ScanModel.get_all(page=page, per_page=per_page,
                                  status=status, match=match, drone_id=drone_id)

    @staticmethod
    def get_by_id(sid: str) -> dict:
        """Busca um scan pelo UUID. Levanta ValueError se não encontrado."""
        row = ScanModel.get_by_id(sid)
        if not row:
            raise ValueError("Scan não encontrado")
        return row

    @staticmethod
    def get_pendentes(page=1, per_page=20) -> list:
        """Retorna a fila de scans pendentes de validação (mais antigos primeiro)."""
        return ScanModel.get_pendentes(page=page, per_page=per_page)

    @staticmethod
    def get_matches(page=1, per_page=20) -> list:
        """Retorna scans com correspondência positiva com veículos roubados."""
        return ScanModel.get_matches(page=page, per_page=per_page)

    @staticmethod
    def get_veiculos(sid: str) -> list:
        """Retorna os veículos vinculados a um scan. Levanta ValueError se não existir."""
        if not ScanModel.get_by_id(sid):
            raise ValueError("Scan não encontrado")
        return ScanModel.get_veiculos(sid)

    @staticmethod
    def create_scan(id_drone: str, raw_placa: str, match: bool,
                    imagem_url=None, latitude=None, longitude=None,
                    modelo=None, cor=None) -> dict:
        """
        Valida a placa e persiste um novo scan no banco.
        Se for um match (informação enriquecida pela API da Pier), já registra
        ou atualiza o veículo real no banco com os dados corretos (modelo e cor).
        """
        from app.services.veiculo_service import VeiculoService

        placa = ScanService._parse_placa(raw_placa)
        scan = Scan(id_drone=id_drone, placa=placa, match=match,
                    imagem_url=imagem_url, latitude=latitude, longitude=longitude)
        
        scan_record = ScanModel.insert(scan.to_db())
        sid = scan_record['id']

        # Se veio com match, a Pier já confirmou que é roubado e temos os dados reais
        if match:
            mod = modelo if modelo else "Desconhecido"
            c = cor if cor else "Indefinida"
            
            try:
                veiculo = VeiculoService.get_by_placa(scan_record['placa'])
                vid = veiculo['id']
                # Atualiza com as infos mais recentes caso a Pier tenha retornado algo novo
                VeiculoService.update_veiculo(vid, raw_modelo=mod, raw_cor=c, roubado=True)
            except ValueError:
                veiculo = VeiculoService.create_veiculo(
                    raw_placa=scan_record['placa'],
                    raw_modelo=mod,
                    raw_cor=c,
                    roubado=True,
                    data_roubo=scan_record['horario_scan']
                )
                vid = veiculo['id']
            
            # Já cria o vínculo entre esse veículo e o scan
            try:
                ScanService.vincular_veiculo(sid, vid)
            except Exception:
                pass

        return scan_record

    @staticmethod
    def validar_scan(sid: str, raw_status: str, validado_por: str, placa=None, cor=None, modelo=None) -> dict:
        """
        Valida o status pelo parser e aplica a decisão humana ao scan.
        Também atualiza placa, cor e modelo se fornecidos.
        Registra o audit log na tabela usuarios_scans.
        Levanta ValueError se o scan não existir ou o status for inválido.
        """
        scan_record = ScanModel.get_by_id(sid)
        if not scan_record:
            raise ValueError("Scan não encontrado")

        status = ScanService._parse_status(raw_status)
        scan = ScanModel.update_validacao(sid, status.get_value(), validado_por, placa=placa, cor=cor, modelo=modelo)

        ScanModel.registrar_acao(
            log_id=str(uuid.uuid4()),
            usuario_id=validado_por,
            scan_id=sid,
            acao=f'validacao:{status.get_value()}'
        )
        return scan

    @staticmethod
    def vincular_veiculo(sid: str, vid: str) -> dict:
        """Vincula um veículo a um scan. Levanta ValueError se o scan não existir."""
        if not ScanModel.get_by_id(sid):
            raise ValueError("Scan não encontrado")
        return ScanModel.vincular_veiculo(sid, vid, link_id=str(uuid.uuid4()))

    @staticmethod
    def get_historico_usuario(usuario_id: str) -> list:
        """Retorna o histórico de ações realizadas por um usuário em scans."""
        return ScanModel.get_historico_usuario(usuario_id)

    @staticmethod
    def delete_scan(sid: str):
        """Remove um scan. Levanta ValueError se não existir."""
        if not ScanModel.delete(sid):
            raise ValueError("Scan não encontrado")
