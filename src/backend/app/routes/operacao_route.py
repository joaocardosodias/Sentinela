from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.decorators import role_required
from app.services.operacao_service import OperacaoService

operacoes_bp = Blueprint('operacoes', __name__, url_prefix='/api/operacoes')


@operacoes_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def listar_operacoes():
    """
    Lista todas as operações com paginação e filtro por status
    ---
    tags:
      - Operações
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
      - name: status
        in: query
        type: string
        description: "Filtrar por status: ativa, pausada, encerrada"
    responses:
      200:
        description: Lista de operações
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status', None)
    rows, total = OperacaoService.get_all(page=page, per_page=per_page, status=status)
    return jsonify({'page': page, 'total': total, 'operacoes': rows}), 200


@operacoes_bp.route('/<string:oid>', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def buscar_operacao(oid):
    """
    Busca uma operação pelo UUID
    ---
    tags:
      - Operações
    security:
      - Bearer: []
    parameters:
      - name: oid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Dados da operação
      404:
        description: Operação não encontrada
    """
    op = OperacaoService.get_by_id(oid)
    if not op:
        return jsonify({'message': 'Operação não encontrada'}), 404
    return jsonify(op), 200


@operacoes_bp.route('/<string:oid>/drones', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def listar_drones_da_operacao(oid):
    """
    Lista todos os drones de uma operação específica
    ---
    tags:
      - Operações
    security:
      - Bearer: []
    parameters:
      - name: oid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Lista de drones da operação
      404:
        description: Operação não encontrada
    """
    if not OperacaoService.get_by_id(oid):
        return jsonify({'message': 'Operação não encontrada'}), 404
    drones = OperacaoService.get_drones(oid)
    return jsonify({'drones': drones, 'total': len(drones)}), 200


@operacoes_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('gestor_remoto')
def criar_operacao():
    """
    Cria uma nova operação de campo
    ---
    tags:
      - Operações
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
            - status
            - localizacao
          properties:
            name:
              type: string
              example: "Operação Centro"
            status:
              type: string
              example: "ativa"
            localizacao:
              type: string
              example: "Avenida Paulista, SP"
    responses:
      201:
        description: Operação criada com sucesso
      400:
        description: Dados inválidos
    """
    data = request.get_json()
    if not data.get('name') or not data.get('status') or not data.get('localizacao'):
        return jsonify({'message': 'name, status e localizacao são obrigatórios'}), 400
    try:
        op = OperacaoService.create_operacao(data['name'], data['status'], data['localizacao'])
        return jsonify({'message': 'Operação criada com sucesso', 'operacao': op}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@operacoes_bp.route('/<string:oid>', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto')
def atualizar_operacao(oid):
    """
    Atualiza nome e/ou status de uma operação
    ---
    tags:
      - Operações
    security:
      - Bearer: []
    parameters:
      - name: oid
        in: path
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            status:
              type: string
              description: "ativa | pausada | encerrada"
            localizacao:
              type: string
    responses:
      200:
        description: Operação atualizada
      404:
        description: Operação não encontrada
    """
    data = request.get_json()
    try:
        op = OperacaoService.update_operacao(
            oid, 
            name=data.get('name'), 
            status=data.get('status'),
            raw_localizacao=data.get('localizacao')
        )
        if not op:
            return jsonify({'message': 'Operação não encontrada'}), 404
        return jsonify({'message': 'Operação atualizada', 'operacao': op}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@operacoes_bp.route('/<string:oid>/status', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto')
def mudar_status_operacao(oid):
    """
    Muda o status de uma operação (atalho rápido)
    ---
    tags:
      - Operações
    security:
      - Bearer: []
    parameters:
      - name: oid
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              example: "encerrada"
    responses:
      200:
        description: Status atualizado
      400:
        description: Status inválido
      404:
        description: Operação não encontrada
    """
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({'message': 'status é obrigatório'}), 400
    try:
        op = OperacaoService.update_operacao(oid, status=status)
        if not op:
            return jsonify({'message': 'Operação não encontrada'}), 404
        return jsonify({'message': f"Status alterado para '{status}'", 'operacao': op}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@operacoes_bp.route('/<string:oid>', methods=['DELETE'])
@jwt_required()
@role_required('gestor_remoto')
def deletar_operacao(oid):
    """
    Remove uma operação (e em cascata todos seus drones e scans)
    ---
    tags:
      - Operações
    security:
      - Bearer: []
    parameters:
      - name: oid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Operação removida
      404:
        description: Operação não encontrada
    """
    try:
        OperacaoService.delete_operacao(oid)
        return jsonify({'message': 'Operação removida com sucesso'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
