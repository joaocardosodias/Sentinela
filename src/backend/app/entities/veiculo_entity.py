class VeiculoPlaca:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class VeiculoModelo:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class VeiculoCor:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class Veiculo:
    def __init__(self, placa: VeiculoPlaca, modelo: VeiculoModelo,
                 cor: VeiculoCor, roubado: bool, data_roubo: str, id: str = None):
        import uuid
        self.__id = str(id) if id else str(uuid.uuid4())
        self.__placa = placa
        self.__modelo = modelo
        self.__cor = cor
        self.__roubado = roubado
        self.__data_roubo = data_roubo

    def get_id(self) -> str:
        return self.__id

    def to_dict(self) -> dict:
        """Serializa o veículo para JSON."""
        return {
            'id': self.__id,
            'placa': self.__placa.get_value(),
            'modelo': self.__modelo.get_value(),
            'cor': self.__cor.get_value(),
            'roubado': self.__roubado,
            'data_roubo': str(self.__data_roubo) if self.__data_roubo else None
        }

    def to_db(self) -> dict:
        """Retorna os dados brutos para uso nos INSERTs e UPDATEs do model."""
        return {
            'id': self.__id,
            'placa': self.__placa.get_value(),
            'modelo': self.__modelo.get_value(),
            'cor': self.__cor.get_value(),
            'roubado': self.__roubado,
            'data_roubo': self.__data_roubo
        }
