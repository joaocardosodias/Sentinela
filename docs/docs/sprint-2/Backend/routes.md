---
sidebar_position: 2
title: Routes
description: Documentação técnica das rotas HTTP com código e parâmetros de requisição.
---

# Routes

O Backend organiza suas rotas em **Blueprints Flask**, um por domínio. Cada Blueprint é registrado no `app/__init__.py` com um prefixo de URL.

Todas as rotas (exceto `POST /api/auth/login`) exigem **JWT Bearer Token** no header `Authorization`. A autorização por cargo (`role`) é controlada pelo decorator `@role_required`.

> **Base URL:** `http://localhost:5000`

> **Swagger UI:** Você pode testar todas as rotas de forma interativa acessando a interface do Swagger. Para isso, basta clicar no atalho **"API UI (Swagger)"** localizado na barra de navegação superior (navbar) deste site.
> Lá dentro, clique no botão verde **Authorize**, insira o token no formato `Bearer {seu_token}` e execute as requisições diretamente pela tela.

---

## Autenticação — `auth_route.py`

Blueprint registrado em `/api/auth`.

---

### `POST /api/auth/login`

A única rota pública do sistema. Recebe e-mail e senha e devolve o **token JWT**.

```python title="app/routes/auth_route.py"
@auth_bp.route('/login', methods=['POST'])
def login():
    # Extrai o payload JSON da requisição HTTP
    data = request.get_json()

    # Verifica se os campos obrigatórios estão presentes no payload
    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400

    try:
        # Chama a camada de serviço para processar a autenticação
        login_data = UserService.login_user(data.get('email'), data.get('password'))
        
        # Retorna o token JWT e o cargo do usuário em caso de sucesso
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'token': login_data['token'],
            'role': login_data['user'].get_role()
        }), 200
    except ValueError as e:
        # Se ocorrer um erro de validação (ex: senha errada), mapeia para o status code correto
        status_code = 401 if "incorreto" in str(e).lower() else 400
        return jsonify({'message': str(e)}), status_code
```

**Exemplo de requisição:**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "gestorremoto@gestorremoto.com", "password": "gestorremoto"}'
```

**Resposta `200`:**

```json
{
  "message": "Login realizado com sucesso!",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "gestor_remoto"
}
```

| Código | Causa |
|--------|-------|
| `200` | Token gerado com sucesso |
| `400` | Campos ausentes ou formato inválido |
| `401` | Credenciais incorretas |

---

### `POST /api/auth/register`

Cria um novo usuário. Restrito a cargos de gestão.

```python title="app/routes/auth_route.py"
@auth_bp.route('/register', methods=['POST'])
@jwt_required() # Protege a rota, exigindo um JWT válido no header
@role_required('gestor_remoto') # Restringe o acesso apenas para gestores remotos
def register():
    # Obtém os dados da requisição
    data = request.get_json()

    # Validação inicial de presença de campos
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Nome, email e senha são obrigatórios'}), 400

    try:
        # Delega a criação para a camada de serviço, que fará as validações de domínio
        new_user = UserService.register_user(
            data.get('name'),
            data.get('email'),
            data.get('password'),
            data.get('role') # Este campo é opcional e possui um valor padrão na camada inferior
        )
        # Retorna o ID gerado confirmando a criação (HTTP 201 Created)
        return jsonify({'message': 'Usuário criado com sucesso', 'id': new_user.get_id()}), 201
    except ValueError as e:
        # Captura regras de negócio não atendidas e retorna como erro na requisição (HTTP 400)
        return jsonify({'message': str(e)}), 400
```

**Body:**

```json
{
  "name": "Maria Souza",
  "email": "maria@empresa.com",
  "password": "senha_segura123",
  "role": "gestor_local"
}
```

---

## Usuários — `user_route.py`

Blueprint registrado em `/api/users`.

---

### `GET /api/users/`

Lista todos os usuários com paginação e filtro opcional por cargo.

```python title="app/routes/user_route.py"
@users_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local') # Permite acesso a ambos os perfis de gestores
def listar_usuarios():
    # Coleta os query parameters da URL e define valores padrão se não fornecidos
    page     = request.args.get('page', 1, type=int)
    # Limita o número máximo de registros por página a 100 para evitar sobrecarga
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    # Filtro opcional por cargo
    role     = request.args.get('role', None)

    # Solicita a lista paginada à camada de serviço
    rows, total = UserService.get_all_users(page=page, per_page=per_page, role=role)
    
    # Formata a resposta com os metadados de paginação
    return jsonify({'page': page, 'per_page': per_page, 'total': total, 'usuarios': rows}), 200
```

**Query Params:** `page` (int), `per_page` (int, máx 100), `role` (string)

---

### `GET /api/users/me`

Retorna o perfil do próprio usuário autenticado. 

```python title="app/routes/user_route.py"
@users_bp.route('/me', methods=['GET'])
@jwt_required() # Requer autenticação
def meu_perfil():
    # Extrai o ID do usuário diretamente do payload decodificado do JWT
    current_user_id = get_jwt_identity()
    try:
        # Busca o perfil na base de dados
        user = UserService.get_user_by_id(current_user_id)
        # O método to_dict() garante que informações sensíveis (como a senha) não sejam expostas
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        # Caso o usuário do token tenha sido deletado
        return jsonify({'message': str(e)}), 404
```

---

### `PATCH /api/users/{user_id}`

Atualiza os dados de um usuário específico.

```python title="app/routes/user_route.py"
@users_bp.route('/<string:user_id>', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def atualizar_usuario(user_id): 
    # O UUID do usuário é extraído da rota (path parameter: user_id)
    data = request.get_json()
    try:
        # Passa os dados recebidos para o serviço processar a atualização
        user = UserService.update_user(
            user_id,
            raw_name=data.get('name'),
            raw_role=data.get('role')
        )
        return jsonify({'message': 'Usuário atualizado com sucesso', 'usuario': user.to_dict()}), 200
    except ValueError as e:
        # Se os campos fornecidos não passarem na validação, retorna 400
        return jsonify({'message': str(e)}), 400
```

---

### `PATCH /api/users/me/password`

Permite ao usuário autenticado atualizar a própria senha.

```python title="app/routes/user_route.py"
@users_bp.route('/me/password', methods=['PATCH'])
@jwt_required()
def atualizar_minha_senha():
    # Obtém o ID do usuário de forma segura via JWT
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # A verificação da senha atual é obrigatória por motivos de segurança
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'message': 'Senha atual e nova senha são obrigatórias'}), 400

    try:
        # O serviço cuidará da verificação do hash antigo e da criação do novo
        UserService.update_password(
            current_user_id,
            data.get('old_password'),
            data.get('new_password')
        )
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
```

---

## Operações — `operacao_route.py`

Blueprint registrado em `/api/operacoes`.

---

### `POST /api/operacoes/`

Cria uma nova operação de campo.

```python title="app/routes/operacao_route.py"
@operacoes_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('gestor_remoto') # Apenas o gestor remoto tem privilégios para criar operações
def criar_operacao():
    data = request.get_json()
    
    # Validação estrutural básica antes de encaminhar para a lógica de negócios
    if not data.get('name') or not data.get('status') or not data.get('created_at') or not data.get('localizacao'):
        return jsonify({'message': 'name, status, localizacao e created_at são obrigatórios'}), 400
        
    try:
        # A validação semântica (ex: se o status existe) ocorre na camada de Serviço
        op = OperacaoService.create_operacao(data['name'], data['status'], data['localizacao'], data['created_at'])
        return jsonify({'message': 'Operação criada com sucesso', 'operacao': op}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
```

**Body:**

```json
{
  "name": "Operação Centro",
  "status": "ativa",
  "localizacao": "Avenida Paulista, SP",
  "created_at": "2024-03-15T08:00:00"
}
```

---

### `PATCH /api/operacoes/{oid}/status`

Altera apenas o status de uma operação.

```python title="app/routes/operacao_route.py"
@operacoes_bp.route('/<string:oid>/status', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto')
def mudar_status_operacao(oid): 
    # Recebe o UUID da operação pela URL
    data   = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({'message': 'status é obrigatório'}), 400
        
    try:
        # Envia apenas o status para ser atualizado, preservando o nome original e outros atributos
        op = OperacaoService.update_operacao(oid, status=status)
        return jsonify({'message': f"Status alterado para '{status}'", 'operacao': op}), 200
    except ValueError as e:
        # Retorna erro caso o status fornecido seja inválido
        return jsonify({'message': str(e)}), 400
```

---

## Drones — `drone_route.py`

Blueprint registrado em `/api/drones`.

---

### `POST /api/drones/`

Registra um novo drone vinculado a uma operação.

```python title="app/routes/drone_route.py"
@drones_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('gestor_remoto')
def criar_drone():
    data = request.get_json()
    
    # Verifica dependências primárias antes do processamento
    if not data.get('operacao_id') or not data.get('nome') or not data.get('status_voo'):
        return jsonify({'message': 'operacao_id, nome e status_voo são obrigatórios'}), 400
        
    try:
        # Passa todos os atributos, incluindo os opcionais extraídos do payload JSON
        drone = DroneService.create_drone(
            data['operacao_id'], data['nome'], data['status_voo'],
            raw_bateria=data.get('bateria'),
            conectividade=data.get('conectividade'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        return jsonify({'message': 'Drone criado com sucesso', 'drone': drone}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
```

**Body:**

```json
{
  "operacao_id": "uuid-da-operacao",
  "nome": "Drone Alpha",
  "status_voo": "pousado",
  "bateria": 100,
  "conectividade": "4G",
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

> Nesta sprint, `latitude` e `longitude` existem no payload por compatibilidade com o schema e como preparação para evoluções futuras. Eles não representam um requisito validado do MVP com o drone Tello.

---

### `PATCH /api/drones/{did}/localizacao`

Rota de atualização de localização/telemetria cadastrada no backend.

```python title="app/routes/drone_route.py"
@drones_bp.route('/<string:did>/localizacao', methods=['PATCH'])
@jwt_required() # Qualquer ator autenticado (incluindo o próprio drone) pode atualizar
def atualizar_localizacao(did):
    data = request.get_json()
    
    # Na implementação atual, latitude e longitude são exigidas pela rota
    if data.get('latitude') is None or data.get('longitude') is None:
        return jsonify({'message': 'latitude e longitude são obrigatórios'}), 400

    try:
        # Atualiza as coordenadas e opcionalmente o nível de bateria atual
        drone = DroneService.update_localizacao(
            did,
            data['latitude'],
            data['longitude'],
            bateria=data.get('bateria')
        )
        # Verifica se o serviço encontrou e atualizou o registro com sucesso
        if not drone:
            return jsonify({'message': 'Drone não encontrado'}), 404
        return jsonify({'message': 'Localização atualizada', 'drone': drone}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
```

> Observação importante: a existência desta rota não significa que a Sprint 2 dependa de GPS real em operação. O backend preserva esse contrato por compatibilidade de modelagem, mas a documentação funcional da sprint considera como fluxo validado o uso de `horario_scan` e `localizacao` da operação.

---

## Scans — `scan_route.py`

Blueprint registrado em `/api/scans`.

---

### `POST /api/scans/`

Endpoint para registrar a detecção de uma placa.

```python title="app/routes/scan_route.py"
@scans_bp.route('/', methods=['POST'])
@jwt_required()
def criar_scan():
    data = request.get_json()
    
    # Validações dos campos base antes de submeter
    if not data.get('id_drone') or not data.get('placa') or data.get('match') is None:
        return jsonify({'message': 'id_drone, placa e match são obrigatórios'}), 400
        
    try:
        # Encaminha os dados do scan e imagens associadas
        scan = ScanService.create_scan(
            data['id_drone'],
            data['placa'].upper(),   # Pré-normalização básica na rota para auxiliar a consulta
            data['match'],
            imagem_url=data.get('imagem_url'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        return jsonify({'message': 'Scan registrado com sucesso', 'scan': scan}), 201
    except Exception as e:
        # Captura erros tanto de negócio (ValueError) quanto exceções imprevistas
        return jsonify({'message': str(e)}), 400
```

**Body:**

```json
{
  "id_drone": "uuid-do-drone",
  "placa": "ABC1D23",
  "match": true,
  "imagem_url": "https://storage.exemplo.com/scans/img123.jpg",
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

> Assim como no cadastro de drones, esses campos aparecem no contrato da API, mas não fazem parte da validação principal do MVP da Sprint 2.

---

### `PATCH /api/scans/{sid}/validar`

Endpoint para tomada de decisão manual sobre um scan.

```python title="app/routes/scan_route.py"
@scans_bp.route('/<string:sid>/validar', methods=['PATCH'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local') # Permite que ambos tipos de operadores validem scans
def validar_scan(sid):
    data = request.get_json()
    
    # Identifica quem está realizando a ação via JWT para fins de auditoria
    current_user_id = get_jwt_identity()
    status = data.get('status_validacao')
    
    if not status:
        return jsonify({'message': 'status_validacao é obrigatório'}), 400
        
    try:
        # Processa a validação enviando o ID do usuário para o log interno da aplicação
        scan = ScanService.validar_scan(sid, status, current_user_id)
        return jsonify({'message': f"Scan marcado como '{status}'", 'scan': scan}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
```

**Body:**

```json
{ "status_validacao": "aprovado" }
```

---

### `GET /api/scans/pendentes`

Recupera os scans ainda não processados.

```python title="app/routes/scan_route.py"
@scans_bp.route('/pendentes', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def scans_pendentes():
    # Parâmetros de navegação em lista paginada
    page     = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Requisita apenas os dados pendentes para revisão humana
    scans    = ScanService.get_pendentes(page=page, per_page=per_page)
    
    return jsonify({'scans': scans, 'total': len(scans)}), 200
```

---

## Veículos — `veiculo_route.py`

Blueprint registrado em `/api/veiculos`.

---

### `POST /api/veiculos/`

Cadastra informações de um novo veículo na base de dados (ex: registro de roubo).

```python title="app/routes/veiculo_route.py"
@veiculos_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('gestor_remoto') # Protege a alteração da base de veículos
def criar_veiculo():
    data     = request.get_json()
    
    # Define a lista de campos que devem obrigatoriamente compor a requisição
    required = ['placa', 'modelo', 'cor', 'roubado', 'data_roubo']
    
    # Verifica se há alguma ausência dentre os campos estritos
    if not all(data.get(k) is not None for k in required):
        return jsonify({'message': f'Campos obrigatórios: {", ".join(required)}'}), 400
        
    try:
        # Efetiva o registro do novo veículo
        veiculo = VeiculoService.create_veiculo(
            data['placa'], data['modelo'], data['cor'],
            data['roubado'], data['data_roubo']
        )
        return jsonify({'message': 'Veículo criado com sucesso', 'veiculo': veiculo}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
```

**Body:**

```json
{
  "placa": "ABC1D23",
  "modelo": "Fiat Uno",
  "cor": "Branco",
  "roubado": true,
  "data_roubo": "2024-03-15T10:30:00"
}
```

---

### `GET /api/veiculos/search?q=...`

Endpoint de pesquisa com suporte a texto parcial.

```python title="app/routes/veiculo_route.py"
@veiculos_bp.route('/search', methods=['GET'])
@jwt_required()
@role_required('gestor_remoto', 'gestor_local')
def buscar_veiculo():
    # Obtém e limpa o texto passado pelo cliente via query parameter "q"
    q = request.args.get('q', '').strip()
    
    try:
        # Dispara a busca utilizando a string de pesquisa 
        resultados = VeiculoService.search(q)
        return jsonify({'resultados': resultados, 'total': len(resultados)}), 200
    except ValueError as e:
        # Trata erros como string de busca demasiado curta
        return jsonify({'message': str(e)}), 400
```
