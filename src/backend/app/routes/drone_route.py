from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.decorators import role_required
from app.services.drone_service import DroneService

drones_bp = Blueprint('drones', __name__, url_prefix='/api/drones')


@drones_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def listar_drones():
    """
    Lista todos os drones com filtros opcionais
    ---
    tags:
      - Drones
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
      - name: operacao_id
        in: query
        type: string
        description: Filtrar por operação
      - name: status_voo
        in: query
        type: string
        description: "em_voo | pousado | offline | manutencao"
    responses:
      200:
        description: Lista de drones
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    operacao_id = request.args.get('operacao_id', None)
    status_voo = request.args.get('status_voo', None)
    rows, total = DroneService.get_all(page=page, per_page=per_page, operacao_id=operacao_id, status_voo=status_voo)
    return jsonify({'page': page, 'total': total, 'drones': rows}), 200


@drones_bp.route('/em-voo', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def drones_em_voo():
    """
    Lista apenas drones atualmente em voo
    ---
    tags:
      - Drones
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de drones em voo
    """
    rows, total = DroneService.get_all(status_voo='em_voo')
    return jsonify({'total': total, 'drones': rows}), 200


@drones_bp.route('/<string:did>', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def buscar_drone(did):
    """
    Busca um drone pelo UUID
    ---
    tags:
      - Drones
    security:
      - Bearer: []
    parameters:
      - name: did
        in: path
        type: string
        required: true
    responses:
      200:
        description: Dados do drone
      404:
        description: Drone não encontrado
    """
    drone = DroneService.get_by_id(did)
    if not drone:
        return jsonify({'message': 'Drone não encontrado'}), 404
    return jsonify(drone), 200


@drones_bp.route('/<string:did>/scans', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def scans_do_drone(did):
    """
    Lista todos os scans realizados por um drone específico
    ---
    tags:
      - Drones
    security:
      - Bearer: []
    parameters:
      - name: did
        in: path
        type: string
        required: true
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
    responses:
      200:
        description: Lista de scans do drone
      404:
        description: Drone não encontrado
    """
    if not DroneService.get_by_id(did):
        return jsonify({'message': 'Drone não encontrado'}), 404
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    scans = DroneService.get_scans(did, page=page, per_page=per_page)
    return jsonify({'scans': scans, 'total': len(scans)}), 200


@drones_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('gestor_remoto')
def criar_drone():
    """
    Adiciona um novo drone a uma operação
    ---
    tags:
      - Drones
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - operacao_id
            - nome
            - status_voo
          properties:
            operacao_id:
              type: string
            nome:
              type: string
              example: "Drone Alpha"
            bateria:
              type: integer
              example: 100
            conectividade:
              type: string
              example: "4G"
            status_voo:
              type: string
              example: "pousado"
            latitude:
              type: number
              example: -23.5505
            longitude:
              type: number
              example: -46.6333
    responses:
      201:
        description: Drone criado com sucesso
      400:
        description: Dados inválidos
    """
    data = request.get_json()
    if not data.get('operacao_id') or not data.get('nome') or not data.get('status_voo'):
        return jsonify({'message': 'operacao_id, nome e status_voo são obrigatórios'}), 400
    try:
        drone = DroneService.create_drone(
            data['operacao_id'], data['nome'], data['status_voo'],
            raw_bateria=data.get('bateria'), conectividade=data.get('conectividade'),
            latitude=data.get('latitude'), longitude=data.get('longitude')
        )
        return jsonify({'message': 'Drone criado com sucesso', 'drone': drone}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@drones_bp.route('/<string:did>', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto')
def atualizar_drone(did):
    """
    Atualiza os dados de um drone
    ---
    tags:
      - Drones
    security:
      - Bearer: []
    parameters:
      - name: did
        in: path
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            nome:
              type: string
            bateria:
              type: integer
            conectividade:
              type: string
            status_voo:
              type: string
    responses:
      200:
        description: Drone atualizado
      404:
        description: Drone não encontrado
    """
    data = request.get_json()
    try:
        drone = DroneService.update_drone(did, **data)
        if not drone:
            return jsonify({'message': 'Drone não encontrado ou sem campos para atualizar'}), 404
        return jsonify({'message': 'Drone atualizado', 'drone': drone}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@drones_bp.route('/<string:did>/localizacao', methods=['PATCH'])
@jwt_required()
def atualizar_localizacao(did):
    """
    Atualiza a localização e bateria de um drone em tempo real
    ---
    tags:
      - Drones
    security:
      - Bearer: []
    parameters:
      - name: did
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
          properties:
            latitude:
              type: number
              example: -23.5505
            longitude:
              type: number
              example: -46.6333
            bateria:
              type: integer
              example: 85
    responses:
      200:
        description: Localização atualizada
      400:
        description: Dados inválidos
      404:
        description: Drone não encontrado
    """
    data = request.get_json()
    if data.get('latitude') is None or data.get('longitude') is None:
        return jsonify({'message': 'latitude e longitude são obrigatórios'}), 400
    drone = DroneService.update_localizacao(did, data['latitude'], data['longitude'], bateria=data.get('bateria'))
    if not drone:
        return jsonify({'message': 'Drone não encontrado'}), 404
    return jsonify({'message': 'Localização atualizada', 'drone': drone}), 200


@drones_bp.route('/<string:did>', methods=['DELETE'])
@jwt_required()
@role_required('gestor_remoto')
def deletar_drone(did):
    """
    Remove um drone do sistema
    ---
    tags:
      - Drones
    security:
      - Bearer: []
    parameters:
      - name: did
        in: path
        type: string
        required: true
    responses:
      200:
        description: Drone removido
      404:
        description: Drone não encontrado
    """
    if not DroneService.delete_drone(did):
        return jsonify({'message': 'Drone não encontrado'}), 404
    return jsonify({'message': 'Drone removido com sucesso'}), 200
