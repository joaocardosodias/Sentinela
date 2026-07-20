import uuid
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from app.entities.user_entity import UserName, UserEmail, UserPassword, UserId, UserRole, User
from app.models.user_model import UserModel


class UserService:

    @staticmethod
    def _parse_name(raw: str) -> UserName:
        """Valida e retorna um UserName. Mínimo 3 caracteres."""
        if not raw or len(raw.strip()) < 3:
            raise ValueError("Nome deve ter ao menos 3 caracteres.")
        return UserName(raw.strip())

    @staticmethod
    def _parse_email(raw: str) -> UserEmail:
        """Valida e retorna um UserEmail. Deve conter @ e ponto."""
        if not raw or '@' not in raw or '.' not in raw:
            raise ValueError("Formato de e-mail inválido.")
        return UserEmail(raw.strip().lower())

    @staticmethod
    def _parse_password(raw: str) -> UserPassword:
        """Valida, aplica hash e retorna um UserPassword. Mínimo 6 caracteres."""
        if not raw or len(raw) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres.")
        return UserPassword(generate_password_hash(raw))

    @staticmethod
    def _parse_role(raw: str) -> UserRole:
        """Valida e retorna um UserRole. Usa gestor_local como padrão se omitido."""
        role = (raw or 'gestor_local').strip().lower()
        if role not in UserRole.VALID:
            raise ValueError(f"Cargo inválido. Use: {', '.join(UserRole.VALID)}")
        return UserRole(role)

    @staticmethod
    def _row_to_user(row: dict) -> User:
        """Converte um dict do banco em um objeto User completo."""
        return User(
            id=UserId(str(row['id'])),
            name=UserName(row['name']),
            email=UserEmail(row['email']),
            password=UserPassword(row['senha']),
            role=UserRole(row['role'])
        )

    @staticmethod
    def register_user(raw_name, raw_email, raw_password, raw_role=None) -> User:
        """
        Cria um novo usuário no sistema.
        Valida todos os campos, verifica duplicidade de e-mail e persiste no banco.
        Levanta ValueError se algum campo for inválido ou o e-mail já existir.
        """
        name = UserService._parse_name(raw_name)
        email = UserService._parse_email(raw_email)
        password = UserService._parse_password(raw_password)
        role = UserService._parse_role(raw_role)

        if UserModel.get_by_email(email.get_value()):
            raise ValueError("E-mail já cadastrado")

        user = User(id=UserId.generate(), name=name, email=email, password=password, role=role)
        UserModel.insert(user.to_db())
        return user

    @staticmethod
    def login_user(raw_email, raw_password) -> dict:
        """
        Autentica o usuário e retorna o token JWT junto com o objeto User.
        Levanta ValueError se o e-mail não existir ou a senha estiver incorreta.
        """
        email = UserService._parse_email(raw_email)
        row = UserModel.get_by_email(email.get_value())

        if not row:
            raise ValueError("E-mail ou senha incorretos")

        user = UserService._row_to_user(row)
        if not user.check_password(raw_password):
            raise ValueError("E-mail ou senha incorretos")

        token = create_access_token(
            identity=user.get_id(),
            additional_claims={'role': user.get_role()}
        )
        return {'token': token, 'user': user}

    @staticmethod
    def get_all_users(page=1, per_page=20, role=None) -> tuple:
        """Retorna lista paginada de usuários. Aceita filtro por cargo."""
        return UserModel.get_all(page=page, per_page=per_page, role=role)

    @staticmethod
    def get_user_by_id(user_id: str) -> User:
        """Busca um usuário pelo UUID. Levanta ValueError se não encontrado."""
        row = UserModel.get_by_id(user_id)
        if not row:
            raise ValueError("Usuário não encontrado")
        return UserService._row_to_user(row)

    @staticmethod
    def update_user(user_id: str, raw_name=None, raw_role=None) -> User:
        """
        Atualiza nome e/ou cargo do usuário após validação pelos parsers.
        Levanta ValueError se o usuário não existir ou os dados forem inválidos.
        """
        row = UserModel.get_by_id(user_id)
        if not row:
            raise ValueError("Usuário não encontrado")

        name_val = UserService._parse_name(raw_name).get_value() if raw_name else None
        role_val = UserService._parse_role(raw_role).get_value() if raw_role else None
        UserModel.update(user_id, name=name_val, role=role_val)
        return UserService.get_user_by_id(user_id)

    @staticmethod
    def update_password(user_id: str, raw_old: str, raw_new: str):
        """
        Troca a senha do usuário após confirmar a senha atual.
        Levanta ValueError se o usuário não existir ou a senha atual estiver errada.
        """
        row = UserModel.get_by_id(user_id)
        if not row:
            raise ValueError("Usuário não encontrado")

        user = UserService._row_to_user(row)
        if not user.check_password(raw_old):
            raise ValueError("Senha atual incorreta")

        hashed = UserService._parse_password(raw_new).get_value()
        UserModel.update_password(user_id, hashed)

    @staticmethod
    def delete_user(user_id: str):
        """Remove permanentemente um usuário. Levanta ValueError se não existir."""
        if not UserModel.get_by_id(user_id):
            raise ValueError("Usuário não encontrado")
        UserModel.delete(user_id)

    @staticmethod
    def search_users(query: str) -> list:
        """Busca usuários pelo nome (mínimo 2 caracteres)."""
        if not query or len(query.strip()) < 2:
            raise ValueError("A busca deve ter ao menos 2 caracteres")
        return UserModel.search_by_name(query.strip())
