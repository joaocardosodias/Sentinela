from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.decorators import role_required
from app.services.veiculo_service import VeiculoService

veiculos_bp = Blueprint('veiculos', __name__, url_prefix='/api/veiculos')


@veiculos_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def listar_veiculos():
    """
    Lista todos os veículos com paginação e filtro por situação de roubo
    ---
    tags:
      - Veículos
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
      - name: roubado
        in: query
        type: boolean
    responses:
      200:
        description: Lista de veículos
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    roubado = request.args.get('roubado', None)
    if roubado is not None:
        roubado = roubado.lower() == 'true'
    rows, total = VeiculoService.get_all(page=page, per_page=per_page, roubado=roubado)
    return jsonify({'page': page, 'per_page': per_page, 'total': total, 'veiculos': rows}), 200


@veiculos_bp.route('/roubados', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def listar_roubados():
    """
    Lista apenas veículos marcados como roubados
    ---
    tags:
      - Veículos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de veículos roubados
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    rows, total = VeiculoService.get_all(page=page, per_page=per_page, roubado=True)
    return jsonify({'page': page, 'total': total, 'veiculos': rows}), 200


@veiculos_bp.route('/search', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def buscar_veiculo():
    """
    Busca veículos por placa, modelo ou cor (parcial, case-insensitive)
    ---
    tags:
      - Veículos
    security:
      - Bearer: []
    parameters:
      - name: q
        in: query
        type: string
        required: true
    responses:
      200:
        description: Resultados da busca
      400:
        description: Parâmetro inválido
    """
    q = request.args.get('q', '').strip()
    try:
        resultados = VeiculoService.search(q)
        return jsonify({'resultados': resultados, 'total': len(resultados)}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@veiculos_bp.route('/placa/<string:placa>', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def buscar_por_placa(placa):
    """
    Busca um veículo pela placa exata
    ---
    tags:
      - Veículos
    security:
      - Bearer: []
    parameters:
      - name: placa
        in: path
        type: string
        required: true
    responses:
      200:
        description: Dados do veículo
      404:
        description: Veículo não encontrado
    """
    try:
        return jsonify(VeiculoService.get_by_placa(placa)), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 404


@veiculos_bp.route('/<string:vid>', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def buscar_por_id(vid):
    """
    Busca um veículo pelo UUID
    ---
    tags:
      - Veículos
    security:
      - Bearer: []
    parameters:
      - name: vid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Dados do veículo
      404:
        description: Veículo não encontrado
    """
    try:
        return jsonify(VeiculoService.get_by_id(vid)), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 404


@veiculos_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('gestor_remoto')
def criar_veiculo():
    """
    Cadastra um novo veículo no sistema
    ---
    tags:
      - Veículos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [placa, modelo, cor, roubado, data_roubo]
          properties:
            placa:
              type: string
              example: "ABC1D23"
            modelo:
              type: string
              example: "Fiat Uno"
            cor:
              type: string
              example: "Branco"
            roubado:
              type: boolean
            data_roubo:
              type: string
              example: "2024-03-15T10:30:00"
    responses:
      201:
        description: Veículo criado com sucesso
      400:
        description: Dados inválidos
    """
    data = request.get_json()
    required = ['placa', 'modelo', 'cor', 'roubado', 'data_roubo']
    if not all(data.get(k) is not None for k in required):
        return jsonify({'message': f'Campos obrigatórios: {", ".join(required)}'}), 400
    try:
        veiculo = VeiculoService.create_veiculo(
            data['placa'], data['modelo'], data['cor'], data['roubado'], data['data_roubo']
        )
        return jsonify({'message': 'Veículo criado com sucesso', 'veiculo': veiculo}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@veiculos_bp.route('/<string:vid>', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto')
def atualizar_veiculo(vid):
    """
    Atualiza os dados de um veículo
    ---
    tags:
      - Veículos
    security:
      - Bearer: []
    parameters:
      - name: vid
        in: path
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            modelo:
              type: string
            cor:
              type: string
            roubado:
              type: boolean
            data_roubo:
              type: string
    responses:
      200:
        description: Veículo atualizado
      400:
        description: Dados inválidos
      404:
        description: Veículo não encontrado
    """
    data = request.get_json()
    try:
        VeiculoService.update_veiculo(vid, **data)
        return jsonify({'message': 'Veículo atualizado com sucesso'}), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e) else 400
        return jsonify({'message': str(e)}), status


@veiculos_bp.route('/<string:vid>', methods=['DELETE'])
@jwt_required()
@role_required('gestor_remoto')
def deletar_veiculo(vid):
    """
    Remove um veículo do sistema
    ---
    tags:
      - Veículos
    security:
      - Bearer: []
    parameters:
      - name: vid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Veículo removido
      404:
        description: Veículo não encontrado
    """
    try:
        VeiculoService.delete_veiculo(vid)
        return jsonify({'message': 'Veículo removido com sucesso'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
