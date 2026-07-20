import uuid


class ScanPlaca:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class ScanStatusValidacao:
    VALID = ['pendente', 'aprovado', 'rejeitado']

    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class Scan:
    def __init__(self, id_drone: str, placa: ScanPlaca, match: bool,
                 status_validacao: ScanStatusValidacao = None,
                 imagem_url: str = None, latitude: float = None,
                 longitude: float = None, id: str = None):
        self.__id = str(id) if id else str(uuid.uuid4())
        self.__id_drone = id_drone
        self.__placa = placa
        self.__match = match
        self.__status_validacao = status_validacao or ScanStatusValidacao('pendente')
        self.__imagem_url = imagem_url
        self.__latitude = latitude
        self.__longitude = longitude

    def get_id(self) -> str:
        return self.__id

    def get_placa(self) -> str:
        return self.__placa.get_value()

    def get_status(self) -> str:
        return self.__status_validacao.get_value()

    def is_match(self) -> bool:
        return self.__match

    def to_dict(self) -> dict:
        """Serializa o scan para JSON."""
        return {
            'id': self.__id,
            'id_drone': self.__id_drone,
            'placa': self.get_placa(),
            'match': self.__match,
            'status_validacao': self.get_status(),
            'imagem_url': self.__imagem_url,
            'latitude': self.__latitude,
            'longitude': self.__longitude
        }

    def to_db(self) -> dict:
        """Retorna os dados brutos para uso nos INSERTs e UPDATEs do model."""
        return {
            'id': self.__id,
            'id_drone': self.__id_drone,
            'placa': self.__placa.get_value(),
            'match': self.__match,
            'imagem_url': self.__imagem_url,
            'latitude': self.__latitude,
            'longitude': self.__longitude
        }
