import uuid
from datetime import datetime
from app.entities.operacao_entity import OperacaoNome, OperacaoStatus, OperacaoLocalizacao, Operacao
from app.models.operacao_model import OperacaoModel


class OperacaoService:

    @staticmethod
    def _parse_nome(raw: str) -> OperacaoNome:
        """Valida o nome da operação: mínimo 3 caracteres."""
        if not raw or len(raw.strip()) < 3:
            raise ValueError("Nome da operação deve ter ao menos 3 caracteres.")
        return OperacaoNome(raw.strip())

    @staticmethod
    def _parse_localizacao(raw: str) -> OperacaoLocalizacao:
        """Valida a localização da operação."""
        if not raw or len(raw.strip()) < 3:
            raise ValueError("Localização da operação deve ter ao menos 3 caracteres.")
        return OperacaoLocalizacao(raw.strip())

    @staticmethod
    def _parse_status(raw: str) -> OperacaoStatus:
        """Valida se o status está entre os valores permitidos."""
        if not raw or raw not in OperacaoStatus.VALID:
            raise ValueError(f"Status inválido. Use: {', '.join(OperacaoStatus.VALID)}")
        return OperacaoStatus(raw)

    @staticmethod
    def get_all(page=1, per_page=20, status=None) -> tuple:
        """Retorna lista paginada de operações. Aceita filtro por status."""
        return OperacaoModel.get_all(page=page, per_page=per_page, status=status)

    @staticmethod
    def get_by_id(oid: str) -> dict:
        """Busca uma operação pelo UUID. Levanta ValueError se não encontrada."""
        row = OperacaoModel.get_by_id(oid)
        if not row:
            raise ValueError("Operação não encontrada")
        return row

    @staticmethod
    def get_drones(oid: str) -> list:
        """Retorna os drones de uma operação. Levanta ValueError se a operação não existir."""
        if not OperacaoModel.get_by_id(oid):
            raise ValueError("Operação não encontrada")
        return OperacaoModel.get_drones(oid)

    @staticmethod
    def create_operacao(raw_name: str, raw_status: str, raw_localizacao: str) -> dict:
        """
        Valida nome, status e localização, e persiste uma nova operação no banco.
        created_at é gerado automaticamente com a data/hora atual.
        Levanta ValueError se os dados forem inválidos.
        """
        nome = OperacaoService._parse_nome(raw_name)
        status = OperacaoService._parse_status(raw_status)
        localizacao = OperacaoService._parse_localizacao(raw_localizacao)
        created_at = datetime.now().isoformat()
        op = Operacao(nome=nome, status=status, localizacao=localizacao, created_at=created_at)
        return OperacaoModel.insert(op.to_db())

    @staticmethod
    def update_operacao(oid: str, raw_name=None, raw_status=None, raw_localizacao=None) -> dict:
        """
        Valida e atualiza nome, status e/ou localização de uma operação.
        Levanta ValueError se a operação não existir ou os dados forem inválidos.
        """
        if not OperacaoModel.get_by_id(oid):
            raise ValueError("Operação não encontrada")
        name_val = OperacaoService._parse_nome(raw_name).get_value() if raw_name else None
        status_val = OperacaoService._parse_status(raw_status).get_value() if raw_status else None
        loc_val = OperacaoService._parse_localizacao(raw_localizacao).get_value() if raw_localizacao else None
        row = OperacaoModel.update(oid, name=name_val, status=status_val, localizacao=loc_val)
        if not row:
            raise ValueError("Nenhum campo para atualizar")
        return row

    @staticmethod
    def delete_operacao(oid: str):
        """Remove uma operação e em cascata seus drones e scans. Levanta ValueError se não existir."""
        if not OperacaoModel.delete(oid):
            raise ValueError("Operação não encontrada")
