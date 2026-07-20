import uuid
from app.entities.drone_entity import DroneNome, DroneStatusVoo, DroneBateria, Drone
from app.models.drone_model import DroneModel


class DroneService:

    @staticmethod
    def _parse_nome(raw: str) -> DroneNome:
        """Valida o nome do drone: mínimo 2 caracteres."""
        if not raw or len(raw.strip()) < 2:
            raise ValueError("Nome do drone deve ter ao menos 2 caracteres.")
        return DroneNome(raw.strip())

    @staticmethod
    def _parse_status_voo(raw: str) -> DroneStatusVoo:
        """Valida se o status de voo está entre os valores permitidos."""
        if not raw or raw not in DroneStatusVoo.VALID:
            raise ValueError(f"Status de voo inválido. Use: {', '.join(DroneStatusVoo.VALID)}")
        return DroneStatusVoo(raw)

    @staticmethod
    def _parse_bateria(raw) -> DroneBateria:
        """Valida o nível de bateria: inteiro entre 0 e 100. Retorna None se omitido."""
        if raw is None:
            return None
        try:
            v = int(raw)
        except (TypeError, ValueError):
            raise ValueError("Bateria deve ser um número inteiro.")
        if v < 0 or v > 100:
            raise ValueError("Bateria deve estar entre 0 e 100.")
        return DroneBateria(v)

    @staticmethod
    def get_all(page=1, per_page=20, operacao_id=None, status_voo=None) -> tuple:
        """Retorna lista paginada de drones com filtros opcionais."""
        return DroneModel.get_all(page=page, per_page=per_page,
                                   operacao_id=operacao_id, status_voo=status_voo)

    @staticmethod
    def get_by_id(did: str) -> dict:
        """Busca um drone pelo UUID. Levanta ValueError se não encontrado."""
        row = DroneModel.get_by_id(did)
        if not row:
            raise ValueError("Drone não encontrado")
        return row

    @staticmethod
    def get_scans(did: str, page=1, per_page=20) -> list:
        """Retorna scans de um drone. Levanta ValueError se o drone não existir."""
        if not DroneModel.get_by_id(did):
            raise ValueError("Drone não encontrado")
        return DroneModel.get_scans(did, page=page, per_page=per_page)

    @staticmethod
    def create_drone(operacao_id: str, raw_nome: str, raw_status_voo: str,
                     raw_bateria=None, conectividade=None, latitude=None, longitude=None) -> dict:
        """
        Valida nome, status e bateria e persiste um novo drone no banco.
        Levanta ValueError se qualquer campo for inválido.
        """
        nome = DroneService._parse_nome(raw_nome)
        status = DroneService._parse_status_voo(raw_status_voo)
        bateria = DroneService._parse_bateria(raw_bateria)

        drone = Drone(
            operacao_id=operacao_id, nome=nome, status_voo=status,
            bateria=bateria, conectividade=conectividade,
            latitude=latitude, longitude=longitude
        )
        return DroneModel.insert(drone.to_db())

    @staticmethod
    def update_drone(did: str, raw_nome=None, raw_status_voo=None,
                     raw_bateria=None, **extra) -> dict:
        """
        Valida os campos e atualiza o drone. Levanta ValueError se não existir ou dados inválidos.
        """
        if not DroneModel.get_by_id(did):
            raise ValueError("Drone não encontrado")

        fields = {**extra}
        if raw_nome:
            fields['nome'] = DroneService._parse_nome(raw_nome).get_value()
        if raw_status_voo:
            fields['status_voo'] = DroneService._parse_status_voo(raw_status_voo).get_value()
        if raw_bateria is not None:
            b = DroneService._parse_bateria(raw_bateria)
            fields['bateria'] = b.get_value() if b else None

        row = DroneModel.update(did, **fields)
        if not row:
            raise ValueError("Nenhum campo válido para atualizar")
        return row

    @staticmethod
    def update_localizacao(did: str, latitude, longitude, raw_bateria=None) -> dict:
        """Atualiza a posição GPS e opcionalmente a bateria do drone."""
        if not DroneModel.get_by_id(did):
            raise ValueError("Drone não encontrado")
        fields = {'latitude': latitude, 'longitude': longitude}
        if raw_bateria is not None:
            b = DroneService._parse_bateria(raw_bateria)
            fields['bateria'] = b.get_value() if b else None
        row = DroneModel.update(did, **fields)
        return row

    @staticmethod
    def delete_drone(did: str):
        """Remove um drone. Levanta ValueError se não existir."""
        if not DroneModel.delete(did):
            raise ValueError("Drone não encontrado")
