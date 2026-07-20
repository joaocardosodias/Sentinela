from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.user_service import UserService
from app.middleware.decorators import role_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ---------------------------------------------------------- #
#  POST /api/auth/register                                    #
#  Cria um novo usuário. Apenas gestores remotos podem fazer. #
# ---------------------------------------------------------- #
@auth_bp.route('/register', methods=['POST'])
@jwt_required()
@role_required('gestor_remoto')
def register():
    """
    Cadastra um novo usuário no sistema
    Rota protegida: apenas gestores remotos autenticados podem criar novos usuários.
    ---
    tags:
      - Autenticação
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: "Maria Souza"
            email:
              type: string
              example: "maria@empresa.com"
            password:
              type: string
              example: "senha_segura123"
            role:
              type: string
              example: "gestor_local"
              description: "Opcional. Se omitido, o usuário será criado como gestor_local."
    responses:
      201:
        description: Usuário criado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
            id:
              type: string
      400:
        description: Dados inválidos ou e-mail já cadastrado
      401:
        description: Token JWT ausente ou inválido
      403:
        description: Apenas gestores remotos podem cadastrar usuários
      500:
        description: Erro interno ao criar o usuário
    """
    data = request.get_json()

    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Nome, email e senha são obrigatórios'}), 400

    try:
        new_user = UserService.register_user(
            data.get('name'),
            data.get('email'),
            data.get('password'),
            data.get('role')
        )
        return jsonify({'message': 'Usuário criado com sucesso', 'id': new_user.get_id()}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


# ---------------------------------------------------------- #
#  POST /api/auth/login                                       #
#  Autentica o usuário e retorna o token JWT                  #
# ---------------------------------------------------------- #
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Autentica um usuário e retorna o token JWT
    Não exige token. Recebe email e senha, e devolve o token de acesso.
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "maria@empresa.com"
            password:
              type: string
              example: "senha_segura123"
    responses:
      200:
        description: Login bem-sucedido, token retornado
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Login realizado com sucesso!"
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            role:
              type: string
              example: "gestor_remoto"
      400:
        description: Campos obrigatórios ausentes ou formato inválido
      401:
        description: E-mail ou senha incorretos
    """
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400

    try:
        login_data = UserService.login_user(data.get('email'), data.get('password'))

        return jsonify({
            'message': 'Login realizado com sucesso!',
            'token': login_data['token'],
            'role': login_data['user'].get_role()
        }), 200
    except ValueError as e:
        status_code = 401 if "incorreto" in str(e).lower() else 400
        return jsonify({'message': str(e)}), status_code
