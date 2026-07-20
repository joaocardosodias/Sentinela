import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.services.user_service import UserService

def init_user():
    app = create_app()
    with app.app_context():
        name = "Gestor Remoto"
        email = "gestorremoto@gestorremoto.com"
        password = "gestorremoto"
        role = "gestor_remoto"

        print(f"Tentando cadastrar usuário: {email}...")
        
        try:
            user = UserService.register_user(
                raw_name=name,
                raw_email=email,
                raw_password=password,
                raw_role=role
            )
            print(f"✅ Usuário criado com sucesso!")
            print(f"ID: {user.get_id()}")
            print(f"Nome: {user.get_name()}")
            print(f"Role: {user.get_role()}")
        except ValueError as e:
            print(f"❌ Erro de validação: {e}")
        except Exception as e:
            print(f"💥 Erro inesperado: {e}")

if __name__ == "__main__":
    init_user()
