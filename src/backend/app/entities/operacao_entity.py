import uuid


class OperacaoNome:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class OperacaoStatus:
    VALID = ['ativa', 'pausada', 'encerrada']

    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class OperacaoLocalizacao:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class Operacao:
    def __init__(self, nome: OperacaoNome, status: OperacaoStatus,
                 localizacao: OperacaoLocalizacao,
                 created_at: str, id: str = None):
        self.__id = str(id) if id else str(uuid.uuid4())
        self.__nome = nome
        self.__status = status
        self.__localizacao = localizacao
        self.__created_at = created_at

    def get_id(self) -> str:
        return self.__id

    def get_nome(self) -> str:
        return self.__nome.get_value()

    def get_status(self) -> str:
        return self.__status.get_value()

    def get_created_at(self) -> str:
        return self.__created_at

    def get_localizacao(self) -> str:
        return self.__localizacao.get_value()

    def to_dict(self) -> dict:
        """Serializa a operação para JSON."""
        return {
            'id': self.__id,
            'name': self.get_nome(),
            'status': self.get_status(),
            'localizacao': self.get_localizacao(),
            'created_at': str(self.__created_at) if self.__created_at else None
        }

    def to_db(self) -> dict:
        """Retorna os dados brutos para uso nos INSERTs e UPDATEs do model."""
        return {
            'id': self.__id,
            'name': self.__nome.get_value(),
            'status': self.__status.get_value(),
            'localizacao': self.__localizacao.get_value(),
            'created_at': self.__created_at
        }
