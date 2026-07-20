---
sidebar_position: 3
title: Services e Casos de Uso
description: Documentação técnica dos services com código real, parsers e regras de negócio de cada domínio.
---

# Services e Casos de Uso

A camada de **Services** é o centro de orquestração da aplicação. Ela é responsável por garantir que nenhum dado bruto chegue à camada de persistência sem antes ter sido validado, transformado em um objeto de domínio e verificado contra as regras de negócio.

Cada service contém dois tipos de métodos:
- **Parsers** (`_parse_xxx`): Funções privadas que validam campos primitivos e os convertem em *Value Objects*. Levantam `ValueError` imediatamente se a regra não for atendida.
- **Casos de Uso** (públicos): Orquestram a sequência completa — parse, composição da entidade e delegação para o model.

> Todos os métodos são `@staticmethod`. Os services não guardam estado; cada chamada é completamente independente.

---

## Autenticação e Usuários — `user_service.py`

Gerencia identidade, autenticação e controle de acesso (RBAC).

---

### Parsers

```python title="app/services/user_service.py"
@staticmethod
def _parse_name(raw: str) -> UserName:
    """Valida e retorna um UserName com mínimo de 3 caracteres."""
    # Remove espaços extras nas bordas antes de medir o comprimento
    if not raw or len(raw.strip()) < 3:
        raise ValueError("Nome deve ter ao menos 3 caracteres.")
    return UserName(raw.strip())

@staticmethod
def _parse_email(raw: str) -> UserEmail:
    """Garante que o e-mail possui estrutura mínima válida e o normaliza em lowercase."""
    # Verifica presença dos delimitadores obrigatórios de um endereço de e-mail
    if not raw or '@' not in raw or '.' not in raw:
        raise ValueError("Formato de e-mail inválido.")
    # Padroniza para lowercase para evitar duplicatas como "User@X.com" e "user@x.com"
    return UserEmail(raw.strip().lower())

@staticmethod
def _parse_password(raw: str) -> UserPassword:
    """Valida o tamanho mínimo e aplica o hash criptográfico antes de armazenar."""
    if not raw or len(raw) < 6:
        raise ValueError("Senha deve ter ao menos 6 caracteres.")
    # A senha nunca é persistida em texto plano — generate_password_hash (werkzeug) gera o bcrypt hash
    return UserPassword(generate_password_hash(raw))

@staticmethod
def _parse_role(raw: str) -> UserRole:
    """Valida o cargo do usuário. Aplica 'gestor_local' como padrão se o campo for omitido."""
    role = (raw or 'gestor_local').strip().lower()
    if role not in UserRole.VALID:
        raise ValueError(f"Cargo inválido. Use: {', '.join(UserRole.VALID)}")
    return UserRole(role)
```

---

### `register_user`

Cria um novo usuário no sistema após validar todos os campos e verificar unicidade do e-mail.

```python title="app/services/user_service.py"
@staticmethod
def register_user(raw_name, raw_email, raw_password, raw_role=None) -> User:
    # 1. Cada campo bruto passa pelo seu parser correspondente
    #    Se qualquer valor for inválido, o ValueError encerra o fluxo aqui mesmo
    name     = UserService._parse_name(raw_name)
    email    = UserService._parse_email(raw_email)
    password = UserService._parse_password(raw_password)  # já retorna o hash, não a string original
    role     = UserService._parse_role(raw_role)

    # 2. Regra de negócio: e-mails devem ser únicos na plataforma
    #    Consulta o banco antes do INSERT para evitar duplicidade
    if UserModel.get_by_email(email.get_value()):
        raise ValueError("E-mail já cadastrado")

    # 3. Composição da entidade — o UUID é gerado aqui, antes do INSERT
    user = User(id=UserId.generate(), name=name, email=email, password=password, role=role)
    UserModel.insert(user.to_db())
    return user
```

---

### `login_user`

Autentica o usuário e emite o token JWT com o cargo embutido nos claims.

```python title="app/services/user_service.py"
@staticmethod
def login_user(raw_email, raw_password) -> dict:
    # 1. Valida o formato do e-mail antes de buscar no banco
    email = UserService._parse_email(raw_email)
    row   = UserModel.get_by_email(email.get_value())

    # 2. Retorna a mesma mensagem genérica para e-mail inexistente e senha errada
    #    Isso evita que um atacante descubra quais e-mails estão cadastrados
    if not row:
        raise ValueError("E-mail ou senha incorretos")

    # 3. Reconstrói o objeto User a partir do dict retornado pelo banco
    user = UserService._row_to_user(row)

    # 4. Compara a senha enviada com o hash armazenado usando werkzeug
    if not user.check_password(raw_password):
        raise ValueError("E-mail ou senha incorretos")

    # 5. Gera o JWT com a identidade (UUID) e o cargo como claim adicional
    #    O cargo é lido nas rotas protegidas pelo @role_required
    token = create_access_token(
        identity=user.get_id(),
        additional_claims={'role': user.get_role()}
    )
    return {'token': token, 'user': user}
```

---

### `update_user` e `update_password`

Atualização de dados cadastrais e troca de senha com verificação da senha atual.

```python title="app/services/user_service.py"
@staticmethod
def update_user(user_id: str, raw_name=None, raw_role=None) -> User:
    # Verifica se o usuário existe antes de tentar qualquer atualização
    row = UserModel.get_by_id(user_id)
    if not row:
        raise ValueError("Usuário não encontrado")

    # Parseia apenas os campos que foram fornecidos — campos omitidos permanecem inalterados
    name_val = UserService._parse_name(raw_name).get_value() if raw_name else None
    role_val = UserService._parse_role(raw_role).get_value() if raw_role else None
    UserModel.update(user_id, name=name_val, role=role_val)
    return UserService.get_user_by_id(user_id)

@staticmethod
def update_password(user_id: str, raw_old: str, raw_new: str):
    row = UserModel.get_by_id(user_id)
    if not row:
        raise ValueError("Usuário não encontrado")

    # Reconstrói o objeto User para ter acesso ao método check_password
    user = UserService._row_to_user(row)

    # Confirma que o usuário conhece a senha atual antes de permitir a troca
    if not user.check_password(raw_old):
        raise ValueError("Senha atual incorreta")

    # Gera e persiste o novo hash da nova senha
    hashed = UserService._parse_password(raw_new).get_value()
    UserModel.update_password(user_id, hashed)
```

---

## Operações — `operacao_service.py`

Gerencia o ciclo de vida das operações de campo às quais os drones são vinculados.

---

### Parsers

```python title="app/services/operacao_service.py"
@staticmethod
def _parse_nome(raw: str) -> OperacaoNome:
    """Garante que a operação tenha um nome descritivo com ao menos 3 caracteres."""
    if not raw or len(raw.strip()) < 3:
        raise ValueError("Nome da operação deve ter ao menos 3 caracteres.")
    return OperacaoNome(raw.strip())

@staticmethod
def _parse_status(raw: str) -> OperacaoStatus:
    """Blinda a coluna de status no banco contra valores arbitrários fora do enum permitido."""
    if not raw or raw not in OperacaoStatus.VALID:
        # VALID contém: 'ativa', 'pausada', 'encerrada'
        raise ValueError(f"Status inválido. Use: {', '.join(OperacaoStatus.VALID)}")
    return OperacaoStatus(raw)

@staticmethod
def _parse_localizacao(raw: str) -> OperacaoLocalizacao:
    """Valida a localização da operação."""
    if not raw or len(raw.strip()) < 3:
        raise ValueError("Localização da operação deve ter ao menos 3 caracteres.")
    return OperacaoLocalizacao(raw.strip())
```

---

### `create_operacao`

Valida nome e status e persiste a nova operação no banco.

```python title="app/services/operacao_service.py"
@staticmethod
def create_operacao(raw_name: str, raw_status: str, raw_localizacao: str, created_at: str) -> dict:
    # 1. Valida os campos de domínio obrigatórios antes de instanciar o objeto
    nome   = OperacaoService._parse_nome(raw_name)
    status = OperacaoService._parse_status(raw_status)
    localizacao = OperacaoService._parse_localizacao(raw_localizacao)

    # 2. A entidade Operacao gera seu próprio UUID internamente
    op = Operacao(nome=nome, status=status, localizacao=localizacao, created_at=created_at)

    # 3. Serializa via to_db() e envia o dicionário para o Model executar o INSERT
    return OperacaoModel.insert(op.to_db())
```

---

### `update_operacao`

Atualiza nome e/ou status. Apenas os campos fornecidos são alterados.

```python title="app/services/operacao_service.py"
@staticmethod
def update_operacao(oid: str, raw_name=None, raw_status=None, raw_localizacao=None) -> dict:
    # Verifica a existência da operação antes de qualquer processamento
    if not OperacaoModel.get_by_id(oid):
        raise ValueError("Operação não encontrada")

    # Parseia apenas os campos enviados — None é passado diretamente ao model para ser ignorado
    name_val   = OperacaoService._parse_nome(raw_name).get_value()   if raw_name   else None
    status_val = OperacaoService._parse_status(raw_status).get_value() if raw_status else None
    loc_val    = OperacaoService._parse_localizacao(raw_localizacao).get_value() if raw_localizacao else None

    row = OperacaoModel.update(oid, name=name_val, status=status_val, localizacao=loc_val)
    if not row:
        raise ValueError("Nenhum campo para atualizar")
    return row
```

---

## Drones — `drone_service.py`

Gerencia o cadastro da frota, o status aeronáutico e a recepção de telemetria em tempo real.

---

### Parsers

```python title="app/services/drone_service.py"
@staticmethod
def _parse_nome(raw: str) -> DroneNome:
    """Valida o nome do drone: mínimo 2 caracteres após remover espaços."""
    if not raw or len(raw.strip()) < 2:
        raise ValueError("Nome do drone deve ter ao menos 2 caracteres.")
    return DroneNome(raw.strip())

@staticmethod
def _parse_status_voo(raw: str) -> DroneStatusVoo:
    """Valida se o status aeronáutico está entre os valores operacionais reconhecidos."""
    if not raw or raw not in DroneStatusVoo.VALID:
        # VALID contém: 'em_voo', 'pousado', 'offline',
        raise ValueError(f"Status de voo inválido. Use: {', '.join(DroneStatusVoo.VALID)}")
    return DroneStatusVoo(raw)

@staticmethod
def _parse_bateria(raw) -> DroneBateria:
    """Valida o nível de bateria recebido como telemetria. Aceita None para campos opcionais."""
    if raw is None:
        # Bateria é opcional no cadastro inicial; None é um valor legítimo
        return None
    try:
        v = int(raw)
    except (TypeError, ValueError):
        # Rejeita strings não numéricas antes de qualquer comparação
        raise ValueError("Bateria deve ser um número inteiro.")
    if v < 0 or v > 100:
        # Rejeita valores fisicamente impossíveis de bateria
        raise ValueError("Bateria deve estar entre 0 e 100.")
    return DroneBateria(v)
```

---

### `create_drone`

Registra um novo drone vinculado a uma operação existente.

```python title="app/services/drone_service.py"
@staticmethod
def create_drone(operacao_id: str, raw_nome: str, raw_status_voo: str,
                 raw_bateria=None, conectividade=None, latitude=None, longitude=None) -> dict:
    # 1. Converte os campos obrigatórios em Value Objects validados
    nome    = DroneService._parse_nome(raw_nome)
    status  = DroneService._parse_status_voo(raw_status_voo)
    bateria = DroneService._parse_bateria(raw_bateria)  # retorna None se não fornecido

    # 2. Instancia a entidade Drone, que gera o UUID internamente
    drone = Drone(
        operacao_id=operacao_id,
        nome=nome,
        status_voo=status,
        bateria=bateria,
        conectividade=conectividade,
        latitude=latitude,
        longitude=longitude
    )
    # 3. Serializa os dados para formato SQL e persiste no banco
    return DroneModel.insert(drone.to_db())
```

---

### `update_drone` e `update_localizacao`

Atualização de dados gerais e atualização de telemetria de posicionamento GPS.

```python title="app/services/drone_service.py"
@staticmethod
def update_drone(did: str, raw_nome=None, raw_status_voo=None, raw_bateria=None, **extra) -> dict:
    # Confirma que o drone existe antes de processar atualizações
    if not DroneModel.get_by_id(did):
        raise ValueError("Drone não encontrado")

    # Monta o dicionário de campos a atualizar dinamicamente
    fields = {**extra}
    if raw_nome:
        fields['nome'] = DroneService._parse_nome(raw_nome).get_value()
    if raw_status_voo:
        fields['status_voo'] = DroneService._parse_status_voo(raw_status_voo).get_value()
    if raw_bateria is not None:
        b = DroneService._parse_bateria(raw_bateria)
        fields['bateria'] = b.get_value() if b else None

    row = DroneModel.update(did, **fields)
    if not row:
        raise ValueError("Nenhum campo válido para atualizar")
    return row

@staticmethod
def update_localizacao(did: str, latitude, longitude, raw_bateria=None) -> dict:
    """Rota de telemetria contínua: chamada em alta frequência pelo firmware do drone."""
    if not DroneModel.get_by_id(did):
        raise ValueError("Drone não encontrado")

    # Sempre atualiza as coordenadas GPS; a bateria é opcional em cada ciclo de telemetria
    fields = {'latitude': latitude, 'longitude': longitude}
    if raw_bateria is not None:
        b = DroneService._parse_bateria(raw_bateria)
        fields['bateria'] = b.get_value() if b else None

    return DroneModel.update(did, **fields)
```

---

## Scans — `scan_service.py`

Processa as detecções de placas realizadas pelos drones e gerencia a fila de validação humana.

---

### Parsers

```python title="app/services/scan_service.py"
@staticmethod
def _parse_placa(raw: str) -> ScanPlaca:
    """Normaliza e valida a placa detectada pelo sistema de visão computacional do drone."""
    if not raw or len(raw.strip()) < 7:
        raise ValueError("Placa inválida. Deve ter ao menos 7 caracteres.")
    # Normaliza para maiúsculas para garantir consistência nas buscas de correspondência
    return ScanPlaca(raw.strip().upper())

@staticmethod
def _parse_status(raw: str) -> ScanStatusValidacao:
    """Restringe o status de validação humana aos três estados possíveis do fluxo de revisão."""
    if not raw or raw not in ScanStatusValidacao.VALID:
        # VALID contém: 'pendente', 'aprovado', 'rejeitado'
        raise ValueError(f"Status inválido. Use: {', '.join(ScanStatusValidacao.VALID)}")
    return ScanStatusValidacao(raw)
```

---

### `create_scan`

Registra a detecção de uma placa realizada pelo drone, com status inicial `pendente`.

```python title="app/services/scan_service.py"
@staticmethod
def create_scan(id_drone: str, raw_placa: str, match: bool,
                imagem_url=None, latitude=None, longitude=None) -> dict:
    # 1. Valida e normaliza a placa antes de construir o objeto Scan
    placa = ScanService._parse_placa(raw_placa)

    # 2. A entidade Scan define status_validacao='pendente' por padrão em seu __init__
    scan = Scan(
        id_drone=id_drone,
        placa=placa,
        match=match,
        imagem_url=imagem_url,
        latitude=latitude,
        longitude=longitude
    )
    # 3. Persiste no banco — o scan entra na fila de revisão humana automaticamente
    return ScanModel.insert(scan.to_db())
```

---

### `validar_scan`

Aplica a decisão humana (aprovado/rejeitado) a um scan e registra a ação no audit log.

```python title="app/services/scan_service.py"
@staticmethod
def validar_scan(sid: str, raw_status: str, validado_por: str) -> dict:
    # 1. Garante que o scan que será julgado ainda existe no banco
    if not ScanModel.get_by_id(sid):
        raise ValueError("Scan não encontrado")

    # 2. Valida o status informado pelo gestor contra os valores aceitos pelo domínio
    status = ScanService._parse_status(raw_status)

    # 3. Persiste a decisão de validação no registro do scan
    scan = ScanModel.update_validacao(sid, status.get_value(), validado_por)

    # 4. Registra no audit log (tabela usuarios_scans) a assinatura completa da ação:
    #    quem validou, qual scan foi revisado, e qual decisão foi tomada
    ScanModel.registrar_acao(
        log_id=str(uuid.uuid4()),   # UUID exclusivo para cada entrada de log
        usuario_id=validado_por,    # ID extraído do JWT pela rota e repassado aqui
        scan_id=sid,
        acao=f'validacao:{status.get_value()}'
    )
    return scan
```

---

### `get_pendentes` e `vincular_veiculo`

Consulta da fila de revisão e vinculação de veículos a scans.

```python title="app/services/scan_service.py"
@staticmethod
def get_pendentes(page=1, per_page=20) -> list:
    """Retorna a fila FIFO de scans aguardando revisão humana (mais antigos primeiro)."""
    # O Model executa ORDER BY horario_scan ASC para garantir a ordem de chegada
    return ScanModel.get_pendentes(page=page, per_page=per_page)

@staticmethod
def vincular_veiculo(sid: str, vid: str) -> dict:
    """Cria a associação entre um scan e um veículo registrado na base."""
    # Verifica se o scan existe antes de criar o vínculo
    if not ScanModel.get_by_id(sid):
        raise ValueError("Scan não encontrado")
    # O ID do vínculo é gerado aqui, no serviço, seguindo o padrão da arquitetura
    return ScanModel.vincular_veiculo(sid, vid, link_id=str(uuid.uuid4()))
```

---

## Veículos — `veiculo_service.py`

Gerencia a base de veículos cadastrados e suas buscas por texto parcial.

---

### Parsers

```python title="app/services/veiculo_service.py"
@staticmethod
def _parse_placa(raw: str) -> VeiculoPlaca:
    """Valida e normaliza a placa do veículo para maiúsculas, garantindo consistência nas buscas."""
    if not raw or len(raw.strip()) < 7:
        raise ValueError("Placa inválida. Deve ter ao menos 7 caracteres.")
    return VeiculoPlaca(raw.strip().upper())

@staticmethod
def _parse_modelo(raw: str) -> VeiculoModelo:
    """Valida o modelo do veículo com comprimento mínimo para evitar registros degenerados."""
    if not raw or len(raw.strip()) < 2:
        raise ValueError("Modelo deve ter ao menos 2 caracteres.")
    return VeiculoModelo(raw.strip())

@staticmethod
def _parse_cor(raw: str) -> VeiculoCor:
    """Valida a cor do veículo com comprimento mínimo."""
    if not raw or len(raw.strip()) < 2:
        raise ValueError("Cor inválida. Deve ter ao menos 2 caracteres.")
    return VeiculoCor(raw.strip())
```

---

### `create_veiculo`

Valida e registra um novo veículo, podendo já marcá-lo como procurado/roubado.

```python title="app/services/veiculo_service.py"
@staticmethod
def create_veiculo(raw_placa, raw_modelo, raw_cor, roubado, data_roubo) -> dict:
    # 1. Todos os campos textuais passam pelos parsers antes de qualquer operação
    placa  = VeiculoService._parse_placa(raw_placa)
    modelo = VeiculoService._parse_modelo(raw_modelo)
    cor    = VeiculoService._parse_cor(raw_cor)

    # 2. Instancia a entidade com os Value Objects e metadados booleanos
    v = Veiculo(placa=placa, modelo=modelo, cor=cor, roubado=roubado, data_roubo=data_roubo)
    VeiculoModel.insert(v.to_db())

    # 3. Retorna o dicionário voltado para a resposta HTTP (to_dict), não para o banco
    return v.to_dict()
```

---

### `search`

Busca veículos por placa, modelo ou cor com texto parcial (case-insensitive).

```python title="app/services/veiculo_service.py"
@staticmethod
def search(query: str) -> list:
    # Impõe comprimento mínimo para evitar queries com ILIKE '%a%' que varrem a tabela inteira
    if not query or len(query.strip()) < 2:
        raise ValueError("A busca deve ter ao menos 2 caracteres")
    # O Model aplica: WHERE placa ILIKE %query% OR modelo ILIKE %query% OR cor ILIKE %query%
    return VeiculoModel.search(query.strip())
```
