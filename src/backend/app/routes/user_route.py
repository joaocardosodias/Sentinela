from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.decorators import role_required
from app.services.user_service import UserService

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


# ---------------------------------------------------------- #
#  GET /api/users/                                            #
#  Lista todos os usuários com paginação e filtro por cargo   #
# ---------------------------------------------------------- #
@users_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto','gestor_local')
def listar_usuarios():
    """
    Lista todos os usuários do sistema
    Suporta paginação e filtro por cargo. Acesso restrito a gestores remotos.
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Número da página
      - name: per_page
        in: query
        type: integer
        default: 20
        description: Quantidade de registros por página (máx. 100)
      - name: role
        in: query
        type: string
        description: "Filtrar por cargo (ex: gestor_local, gestor_remoto)"
    responses:
      200:
        description: Lista paginada de usuários
      401:
        description: Token JWT ausente ou inválido
      403:
        description: Cargo insuficiente
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    role = request.args.get('role', None)

    rows, total = UserService.get_all_users(page=page, per_page=per_page, role=role)
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'usuarios': rows
    }), 200


# ---------------------------------------------------------- #
#  GET /api/users/me                                          #
#  Retorna os dados do próprio usuário logado                 #
# ---------------------------------------------------------- #
@users_bp.route('/me', methods=['GET'])
@jwt_required()
def meu_perfil():
    """
    Retorna os dados do usuário autenticado
    Qualquer usuário com token válido pode ver o próprio perfil.
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    responses:
      200:
        description: Dados do usuário logado
      401:
        description: Token JWT ausente ou inválido
      404:
        description: Usuário não encontrado
    """
    current_user_id = get_jwt_identity()
    try:
        user = UserService.get_user_by_id(current_user_id)
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 404


# ---------------------------------------------------------- #
#  GET /api/users/search?q=...                                #
#  Busca usuários por nome (parcial, case-insensitive)        #
# ---------------------------------------------------------- #
@users_bp.route('/search', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto','gestor_local')
def buscar_usuarios():
    """
    Busca usuários pelo nome (parcial)
    Realiza uma busca case-insensitive pelo nome informado.
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Termo de busca (mínimo 2 caracteres)
    responses:
      200:
        description: Usuários encontrados
      400:
        description: Parâmetro de busca inválido
      401:
        description: Token JWT ausente ou inválido
      403:
        description: Cargo insuficiente
    """
    q = request.args.get('q', '')
    try:
        resultados = UserService.search_users(q)
        return jsonify({'resultados': resultados, 'total': len(resultados)}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


# ---------------------------------------------------------- #
#  GET /api/users/<id>                                        #
#  Busca um usuário específico pelo UUID                      #
# ---------------------------------------------------------- #
@users_bp.route('/<string:user_id>', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto','gestor_local')
def buscar_por_id(user_id):
    """
    Busca um usuário pelo seu UUID
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: UUID do usuário
    responses:
      200:
        description: Dados do usuário encontrado
      401:
        description: Token JWT ausente ou inválido
      403:
        description: Cargo insuficiente
      404:
        description: Usuário não encontrado
    """
    try:
        user = UserService.get_user_by_id(user_id)
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 404


# ---------------------------------------------------------- #
#  PATCH /api/users/<id>                                      #
#  Atualiza nome e/ou cargo de um usuário                     #
# ---------------------------------------------------------- #
@users_bp.route('/<string:user_id>', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto','gestor_local')
def atualizar_usuario(user_id):
    """
    Atualiza os dados de um usuário (name e/ou role)
    Apenas gestores remotos ou gestores locais podem alterar dados de outros usuários.
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: UUID do usuário a ser atualizado
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
              example: "João Silva Atualizado"
            role:
              type: string
              example: "gestor_remoto"
    responses:
      200:
        description: Usuário atualizado com sucesso
      400:
        description: Dados inválidos
      401:
        description: Token JWT ausente ou inválido
      403:
        description: Cargo insuficiente
      404:
        description: Usuário não encontrado
    """
    data = request.get_json()
    try:
        user = UserService.update_user(
            user_id,
            raw_name=data.get('name'),
            raw_role=data.get('role')
        )
        return jsonify({'message': 'Usuário atualizado com sucesso', 'usuario': user.to_dict()}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


# ---------------------------------------------------------- #
#  PATCH /api/users/me/password                               #
#  O próprio usuário altera sua senha                         #
# ---------------------------------------------------------- #
@users_bp.route('/me/password', methods=['PATCH'])
@jwt_required()
def atualizar_minha_senha():
    """
    Atualiza a senha do próprio usuário autenticado
    Exige a senha atual para confirmar a operação.
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - old_password
            - new_password
          properties:
            old_password:
              type: string
              example: "senha_antiga123"
            new_password:
              type: string
              example: "nova_senha_forte456"
    responses:
      200:
        description: Senha alterada com sucesso
      400:
        description: Senha atual incorreta ou nova senha inválida
      401:
        description: Token JWT ausente ou inválido
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'message': 'Senha atual e nova senha são obrigatórias'}), 400

    try:
        UserService.update_password(
            current_user_id,
            data.get('old_password'),
            data.get('new_password')
        )
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


# ---------------------------------------------------------- #
#  DELETE /api/users/<id>                                     #
#  Remove um usuário do sistema                               #
# ---------------------------------------------------------- #
@users_bp.route('/<string:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('gestor_remoto')
def deletar_usuario(user_id):
    """
    Remove um usuário do sistema permanentemente
    Esta ação é irreversível. Restrita a gestores remotos.
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: UUID do usuário a ser removido
    responses:
      200:
        description: Usuário removido com sucesso
      401:
        description: Token JWT ausente ou inválido
      403:
        description: Cargo insuficiente
      404:
        description: Usuário não encontrado
    """
    try:
        UserService.delete_user(user_id)
        return jsonify({'message': 'Usuário removido com sucesso'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
