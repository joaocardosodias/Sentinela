from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.decorators import role_required
from app.services.scan_service import ScanService

scans_bp = Blueprint('scans', __name__, url_prefix='/api/scans')


@scans_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def listar_scans():
    """
    Lista todos os scans com filtros e paginação
    ---
    tags:
      - Scans
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
        description: "pendente | aprovado | rejeitado | limpo"
      - name: match
        in: query
        type: boolean
        description: "Filtrar por se houve match com veículo roubado"
      - name: drone_id
        in: query
        type: string
        description: "UUID do drone"
    responses:
      200:
        description: Lista de scans
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status', None)
    drone_id = request.args.get('drone_id', None)
    match = request.args.get('match', None)
    if match is not None:
        match = match.lower() == 'true'
    rows, total = ScanService.get_all(page=page, per_page=per_page, status=status, match=match, drone_id=drone_id)
    return jsonify({'page': page, 'total': total, 'scans': rows}), 200


@scans_bp.route('/pendentes', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def scans_pendentes():
    """
    Lista scans aguardando validação humana (os mais antigos primeiro)
    ---
    tags:
      - Scans
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
    responses:
      200:
        description: Lista de scans pendentes
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    scans = ScanService.get_pendentes(page=page, per_page=per_page)
    return jsonify({'scans': scans, 'total': len(scans)}), 200


@scans_bp.route('/matches', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def scans_com_match():
    """
    Lista scans onde houve correspondência com veículo roubado
    ---
    tags:
      - Scans
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
    responses:
      200:
        description: Lista de scans com match
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    scans = ScanService.get_matches(page=page, per_page=per_page)
    return jsonify({'scans': scans, 'total': len(scans)}), 200


@scans_bp.route('/<string:sid>', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def buscar_scan(sid):
    """
    Busca um scan pelo UUID
    ---
    tags:
      - Scans
    security:
      - Bearer: []
    parameters:
      - name: sid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Dados do scan
      404:
        description: Scan não encontrado
    """
    scan = ScanService.get_by_id(sid)
    if not scan:
        return jsonify({'message': 'Scan não encontrado'}), 404
    return jsonify(scan), 200


@scans_bp.route('/<string:sid>/veiculos', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def veiculos_do_scan(sid):
    """
    Lista os veículos vinculados a um scan
    ---
    tags:
      - Scans
    security:
      - Bearer: []
    parameters:
      - name: sid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Veículos relacionados ao scan
      404:
        description: Scan não encontrado
    """
    if not ScanService.get_by_id(sid):
        return jsonify({'message': 'Scan não encontrado'}), 404
    veiculos = ScanService.get_veiculos(sid)
    return jsonify({'veiculos': veiculos, 'total': len(veiculos)}), 200


@scans_bp.route('/', methods=['POST'])
@jwt_required()
def criar_scan():
    """
    Registra um novo scan realizado por um drone
    Rota usada pelo firmware do drone ou pelo sistema de processamento de imagem.
    ---
    tags:
      - Scans
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - id_drone
            - placa
            - match
          properties:
            id_drone:
              type: string
            placa:
              type: string
              example: "ABC1D23"
            match:
              type: boolean
              example: true
            imagem_url:
              type: string
              example: "https://storage.exemplo.com/scans/img123.jpg"
            latitude:
              type: number
              example: -23.5505
            longitude:
              type: number
              example: -46.6333
    responses:
      201:
        description: Scan registrado com sucesso
      400:
        description: Dados inválidos
    """
    data = request.get_json()
    if not data.get('id_drone') or not data.get('placa') or data.get('match') is None:
        return jsonify({'message': 'id_drone, placa e match são obrigatórios'}), 400
    try:
        scan = ScanService.create_scan(
            data['id_drone'], data['placa'].upper(), data['match'],
            imagem_url=data.get('imagem_url'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            modelo=data.get('modelo'),
            cor=data.get('cor')
        )
        return jsonify({'message': 'Scan registrado com sucesso', 'scan': scan}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

@scans_bp.route('/<string:sid>/validar', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def validar_scan(sid):
    """
    Valida (aprova ou rejeita) um scan pendente
    ---
    tags:
      - Scans
    security:
      - Bearer: []
    parameters:
      - name: sid
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status_validacao
          properties:
            status_validacao:
              type: string
              example: "aprovado"
              description: "aprovado | rejeitado"
            placa:
              type: string
              example: "ABC1D23"
              description: "Placa editada (opcional)"
            cor:
              type: string
              example: "Preto"
              description: "Cor do veículo (opcional)"
            modelo:
              type: string
              example: "Honda Civic"
              description: "Modelo do veículo (opcional)"
    responses:
      200:
        description: Scan validado com sucesso
      400:
        description: Status inválido
      404:
        description: Scan não encontrado
    """
    data = request.get_json() or {}
    current_user_id = get_jwt_identity()
    status = data.get('status_validacao')
    if not status:
        return jsonify({'message': 'status_validacao é obrigatório'}), 400
    try:
        scan = ScanService.validar_scan(
            sid, 
            status, 
            current_user_id,
            placa=data.get('placa'),
            cor=data.get('cor'),
            modelo=data.get('modelo')
        )
        if not scan:
            return jsonify({'message': 'Scan não encontrado'}), 404
        return jsonify({'message': f"Scan marcado como '{status}'", 'scan': scan}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400



@scans_bp.route('/<string:sid>/vincular-veiculo', methods=['POST'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def vincular_veiculo(sid):
    """
    Vincula um veículo a um scan (tabela veiculos_scans)
    ---
    tags:
      - Scans
    security:
      - Bearer: []
    parameters:
      - name: sid
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - veiculo_id
          properties:
            veiculo_id:
              type: string
    responses:
      201:
        description: Veículo vinculado ao scan
      400:
        description: Dados inválidos
    """
    data = request.get_json()
    if not data.get('veiculo_id'):
        return jsonify({'message': 'veiculo_id é obrigatório'}), 400
    try:
        vinculo = ScanService.vincular_veiculo(sid, data['veiculo_id'])
        return jsonify({'message': 'Veículo vinculado ao scan', 'vinculo': vinculo}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@scans_bp.route('/historico/usuario/<string:uid>', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto')
def historico_usuario(uid):
    """
    Lista o histórico de ações realizadas por um usuário em scans
    ---
    tags:
      - Scans
    security:
      - Bearer: []
    parameters:
      - name: uid
        in: path
        type: string
        required: true
        description: UUID do usuário
    responses:
      200:
        description: Histórico de ações do usuário
    """
    historico = ScanService.get_historico_usuario(uid)
    return jsonify({'historico': historico, 'total': len(historico)}), 200


@scans_bp.route('/<string:sid>', methods=['DELETE'])
@jwt_required()
@role_required('gestor_remoto')
def deletar_scan(sid):
    """
    Remove um scan do sistema
    ---
    tags:
      - Scans
    security:
      - Bearer: []
    parameters:
      - name: sid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Scan removido
      404:
        description: Scan não encontrado
    """
    if not ScanService.delete_scan(sid):
        return jsonify({'message': 'Scan não encontrado'}), 404
    return jsonify({'message': 'Scan removido com sucesso'}), 200
