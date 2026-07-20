import uuid
from app.entities.veiculo_entity import VeiculoPlaca, VeiculoModelo, VeiculoCor, Veiculo
from app.models.veiculo_model import VeiculoModel


class VeiculoService:

    @staticmethod
    def _parse_placa(raw: str) -> VeiculoPlaca:
        """Valida a placa: mínimo 7 caracteres, convertida para maiúsculas."""
        if not raw or len(raw.strip()) < 7:
            raise ValueError("Placa inválida. Deve ter ao menos 7 caracteres.")
        return VeiculoPlaca(raw.strip().upper())

    @staticmethod
    def _parse_modelo(raw: str) -> VeiculoModelo:
        """Valida o modelo do veículo: mínimo 2 caracteres."""
        if not raw or len(raw.strip()) < 2:
            raise ValueError("Modelo deve ter ao menos 2 caracteres.")
        return VeiculoModelo(raw.strip())

    @staticmethod
    def _parse_cor(raw: str) -> VeiculoCor:
        """Valida a cor do veículo: mínimo 2 caracteres."""
        if not raw or len(raw.strip()) < 2:
            raise ValueError("Cor inválida. Deve ter ao menos 2 caracteres.")
        return VeiculoCor(raw.strip())

    @staticmethod
    def get_all(page=1, per_page=20, roubado=None) -> tuple:
        """Retorna lista paginada de veículos. Aceita filtro por status de roubo."""
        return VeiculoModel.get_all(page=page, per_page=per_page, roubado=roubado)

    @staticmethod
    def get_by_id(vid: str) -> dict:
        """Busca um veículo pelo UUID. Levanta ValueError se não encontrado."""
        row = VeiculoModel.get_by_id(vid)
        if not row:
            raise ValueError("Veículo não encontrado")
        return row

    @staticmethod
    def get_by_placa(placa: str) -> dict:
        """Busca um veículo pela placa. Levanta ValueError se não encontrado."""
        row = VeiculoModel.get_by_placa(placa.upper())
        if not row:
            raise ValueError("Veículo não encontrado")
        return row

    @staticmethod
    def search(query: str) -> list:
        """Busca veículos por placa, modelo ou cor (mínimo 2 caracteres)."""
        if not query or len(query.strip()) < 2:
            raise ValueError("A busca deve ter ao menos 2 caracteres")
        return VeiculoModel.search(query.strip())

    @staticmethod
    def create_veiculo(raw_placa, raw_modelo, raw_cor, roubado, data_roubo) -> dict:
        """
        Valida todos os campos, cria o objeto Veiculo e persiste no banco.
        Levanta ValueError se qualquer campo for inválido.
        """
        placa = VeiculoService._parse_placa(raw_placa)
        modelo = VeiculoService._parse_modelo(raw_modelo)
        cor = VeiculoService._parse_cor(raw_cor)

        v = Veiculo(placa=placa, modelo=modelo, cor=cor, roubado=roubado, data_roubo=data_roubo)
        VeiculoModel.insert(v.to_db())
        return v.to_dict()

    @staticmethod
    def update_veiculo(vid: str, raw_placa=None, raw_modelo=None,
                       raw_cor=None, roubado=None, data_roubo=None):
        """
        Valida e atualiza os campos fornecidos de um veículo.
        Levanta ValueError se o veículo não existir ou os dados forem inválidos.
        """
        if not VeiculoModel.get_by_id(vid):
            raise ValueError("Veículo não encontrado")

        placa_val = VeiculoService._parse_placa(raw_placa).get_value() if raw_placa else None
        modelo_val = VeiculoService._parse_modelo(raw_modelo).get_value() if raw_modelo else None
        cor_val = VeiculoService._parse_cor(raw_cor).get_value() if raw_cor else None
        VeiculoModel.update(vid, placa=placa_val, modelo=modelo_val, cor=cor_val,
                            roubado=roubado, data_roubo=data_roubo)

    @staticmethod
    def delete_veiculo(vid: str):
        """Remove um veículo. Levanta ValueError se não existir."""
        if not VeiculoModel.get_by_id(vid):
            raise ValueError("Veículo não encontrado")
        VeiculoModel.delete(vid)
