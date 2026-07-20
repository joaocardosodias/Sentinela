import uuid
from werkzeug.security import check_password_hash


class UserName:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class UserEmail:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class UserPassword:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value

    def verify(self, raw: str) -> bool:
        """Compara a senha bruta com o hash armazenado."""
        return check_password_hash(self.__value, raw)


class UserId:
    def __init__(self, value: str):
        self.__value = str(value)

    @classmethod
    def generate(cls) -> 'UserId':
        """Gera um novo UUID aleatório."""
        return cls(str(uuid.uuid4()))

    def get_value(self) -> str:
        return self.__value


class UserRole:
    VALID = ["gestor_local", "gestor_remoto"]

    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class User:
    def __init__(self, id: UserId, name: UserName, email: UserEmail,
                 password: UserPassword, role: UserRole):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__password = password
        self.__role = role

    def get_id(self) -> str:
        return self.__id.get_value()

    def get_name(self) -> str:
        return self.__name.get_value()

    def get_email(self) -> str:
        return self.__email.get_value()

    def get_role(self) -> str:
        return self.__role.get_value()

    def check_password(self, raw: str) -> bool:
        """Verifica se a senha bruta corresponde ao hash armazenado."""
        return self.__password.verify(raw)

    def to_dict(self) -> dict:
        """Serializa o usuário para JSON (sem expor a senha)."""
        return {
            'id': self.get_id(),
            'name': self.get_name(),
            'email': self.get_email(),
            'role': self.get_role()
        }

    def to_db(self) -> dict:
        """Retorna os dados brutos para uso nos INSERTs e UPDATEs do model."""
        return {
            'id': self.__id.get_value(),
            'name': self.__name.get_value(),
            'email': self.__email.get_value(),
            'senha': self.__password.get_value(),
            'role': self.__role.get_value()
        }
