import uuid


class DroneNome:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class DroneStatusVoo:
    VALID = ['em_voo', 'pousado', 'offline']

    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class DroneBateria:
    def __init__(self, value: int):
        self.__value = value

    def get_value(self) -> int:
        return self.__value


class Drone:
    def __init__(self, operacao_id: str, nome: DroneNome, status_voo: DroneStatusVoo,
                 bateria: DroneBateria = None, conectividade: str = None,
                 latitude: float = None, longitude: float = None, id: str = None):
        self.__id = str(id) if id else str(uuid.uuid4())
        self.__operacao_id = operacao_id
        self.__nome = nome
        self.__status_voo = status_voo
        self.__bateria = bateria
        self.__conectividade = conectividade
        self.__latitude = latitude
        self.__longitude = longitude

    def get_id(self) -> str:
        return self.__id

    def get_nome(self) -> str:
        return self.__nome.get_value()

    def get_status_voo(self) -> str:
        return self.__status_voo.get_value()

    def get_bateria(self):
        return self.__bateria.get_value() if self.__bateria else None

    def to_dict(self) -> dict:
        """Serializa o drone para JSON."""
        return {
            'id': self.__id,
            'operacao_id': self.__operacao_id,
            'nome': self.get_nome(),
            'status_voo': self.get_status_voo(),
            'bateria': self.get_bateria(),
            'conectividade': self.__conectividade,
            'latitude': self.__latitude,
            'longitude': self.__longitude
        }

    def to_db(self) -> dict:
        """Retorna os dados brutos para uso nos INSERTs e UPDATEs do model."""
        return {
            'id': self.__id,
            'operacao_id': self.__operacao_id,
            'nome': self.__nome.get_value(),
            'status_voo': self.__status_voo.get_value(),
            'bateria': self.__bateria.get_value() if self.__bateria else None,
            'conectividade': self.__conectividade,
            'latitude': self.__latitude,
            'longitude': self.__longitude
        }
