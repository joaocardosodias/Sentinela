---
sidebar_position: 4
title: Entities e Value Objects
description: Documentação das classes de domínio puro — Value Objects e Entidades — com código real e comentários explicativos.
---

# Entities e Value Objects

A camada de **Entities** é o núcleo do sistema. Ela contém as definições estruturais do domínio sem qualquer dependência de banco de dados, protocolo HTTP ou framework externo.

Cada arquivo de entidade é composto por dois tipos de classe:

- **Value Objects**: Representam um único atributo com semântica própria. São imutáveis — uma vez criados, seu valor interno não pode ser alterado. Exemplos: `DroneNome`, `UserEmail`, `ScanPlaca`.
- **Entidades**: Agregam Value Objects para representar um objeto completo do domínio com identidade própria (UUID). Expõem `to_dict()` para respostas HTTP e `to_db()` para persistência SQL.

> As entidades não sabem que um banco de dados existe. Não há nenhum `import psycopg2` aqui.

---

## Usuários — `user_entity.py`

---

### Value Objects

```python title="app/entities/user_entity.py"
class UserName:
    def __init__(self, value: str):
        # O valor é armazenado como atributo privado (name mangling __value)
        # Isso impede acesso direto de fora: user_name.__value lança AttributeError
        self.__value = value

    def get_value(self) -> str:
        # Único ponto de acesso ao valor encapsulado
        return self.__value


class UserEmail:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class UserPassword:
    def __init__(self, value: str):
        # O valor aqui já é o hash bcrypt, não a senha em texto puro
        # Nenhuma parte do sistema acessa a senha original após o parse
        self.__value = value

    def get_value(self) -> str:
        # Retorna o hash — nunca a senha original
        return self.__value

    def verify(self, raw: str) -> bool:
        """Compara uma string bruta com o hash armazenado usando check_password_hash do werkzeug."""
        # werkzeug sabe reconstituir o salt e comparar corretamente com o hash
        return check_password_hash(self.__value, raw)


class UserId:
    def __init__(self, value: str):
        self.__value = str(value)

    @classmethod
    def generate(cls) -> 'UserId':
        """Factory method: instancia um UserId com UUID v4 gerado pelo Python."""
        # O ID nasce aqui, antes do INSERT — independente do banco de dados
        return cls(str(uuid.uuid4()))

    def get_value(self) -> str:
        return self.__value


class UserRole:
    # A lista de cargos válidos é definida no próprio tipo, como invariante de domínio
    VALID = ["gestor_local", "gestor_remoto"]

    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value
```

---

### Entidade `User`

```python title="app/entities/user_entity.py"
class User:
    def __init__(self, id: UserId, name: UserName, email: UserEmail,
                 password: UserPassword, role: UserRole):
        # A entidade recebe apenas Value Objects — nunca strings brutas
        # Isso garante que qualquer User instanciado já possui dados válidos
        self.__id       = id
        self.__name     = name
        self.__email    = email
        self.__password = password
        self.__role     = role

    def get_id(self) -> str:
        return self.__id.get_value()

    def get_name(self) -> str:
        return self.__name.get_value()

    def get_email(self) -> str:
        return self.__email.get_value()

    def get_role(self) -> str:
        return self.__role.get_value()

    def check_password(self, raw: str) -> bool:
        """Delega a verificação criptográfica ao próprio Value Object UserPassword."""
        # A lógica de hash fica encapsulada dentro do Value Object, não espalhada pelo código
        return self.__password.verify(raw)

    def to_dict(self) -> dict:
        """Serializa o usuário para resposta HTTP — a senha nunca é incluída."""
        return {
            'id':    self.get_id(),
            'name':  self.get_name(),
            'email': self.get_email(),
            'role':  self.get_role()
            # 'senha' ausente intencionalmente: dados de segurança não são expostos via API
        }

    def to_db(self) -> dict:
        """Serializa para o INSERT/UPDATE no banco — inclui a hash da senha."""
        return {
            'id':    self.__id.get_value(),
            'name':  self.__name.get_value(),
            'email': self.__email.get_value(),
            'senha': self.__password.get_value(),  # hash bcrypt, nunca texto puro
            'role':  self.__role.get_value()
        }
```

**Diferença entre `to_dict()` e `to_db()`:** `to_dict()` omite a senha por segurança (resposta para o cliente); `to_db()` inclui o hash porque o banco precisa armazená-lo.

---

## Operações — `operacao_entity.py`

---

### Value Objects

```python title="app/entities/operacao_entity.py"
class OperacaoNome:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class OperacaoStatus:
    # Enum de domínio: os únicos estados que uma operação pode assumir
    VALID = ['ativa', 'pausada', 'encerrada']

    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class OperacaoLocalizacao:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value
```

---

### Entidade `Operacao`

```python title="app/entities/operacao_entity.py"
class Operacao:
    def __init__(self, nome: OperacaoNome, status: OperacaoStatus,
                 localizacao: OperacaoLocalizacao,
                 created_at: str, id: str = None):
        # Se id não for fornecido (criação nova), gera UUID aqui mesmo
        # Se id for fornecido (reconstrução a partir do banco), usa o existente
        self.__id        = str(id) if id else str(uuid.uuid4())
        self.__nome      = nome
        self.__status    = status
        self.__localizacao = localizacao
        self.__created_at = created_at

    def get_id(self) -> str:
        return self.__id

    def get_nome(self) -> str:
        return self.__nome.get_value()

    def get_status(self) -> str:
        return self.__status.get_value()

    def get_localizacao(self) -> str:
        return self.__localizacao.get_value()

    def to_dict(self) -> dict:
        """Formato de resposta HTTP — datas são convertidas para string."""
        return {
            'id':         self.__id,
            'name':       self.get_nome(),
            'status':     self.get_status(),
            'localizacao': self.get_localizacao(),
            'created_at': str(self.__created_at) if self.__created_at else None
        }

    def to_db(self) -> dict:
        """Formato de persistência — tipos nativos para compatibilidade com psycopg2."""
        return {
            'id':         self.__id,
            'name':       self.__nome.get_value(),
            'status':     self.__status.get_value(),
            'localizacao': self.__localizacao.get_value(),
            'created_at': self.__created_at
        }
```

---

## Drones — `drone_entity.py`

---

### Value Objects

```python title="app/entities/drone_entity.py"
class DroneNome:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class DroneStatusVoo:
    # Os únicos estados operacionais reconhecidos pelo domínio
    VALID = ['em_voo', 'pousado', 'offline']

    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class DroneBateria:
    def __init__(self, value: int):
        # O valor já chegou validado (entre 0 e 100) — o Value Object apenas encapsula
        self.__value = value

    def get_value(self) -> int:
        # Retorna int, não string — importante para o JSON serializer tratar corretamente
        return self.__value
```

---

### Entidade `Drone`

```python title="app/entities/drone_entity.py"
class Drone:
    def __init__(self, operacao_id: str, nome: DroneNome, status_voo: DroneStatusVoo,
                 bateria: DroneBateria = None, conectividade: str = None,
                 latitude: float = None, longitude: float = None, id: str = None):
        # UUID gerado pelo Python na criação; preservado quando reconstruído do banco
        self.__id           = str(id) if id else str(uuid.uuid4())
        self.__operacao_id  = operacao_id
        self.__nome         = nome
        self.__status_voo   = status_voo
        # Campos opcionais: bateria, conectividade e coordenadas podem ser None
        self.__bateria      = bateria
        self.__conectividade = conectividade
        self.__latitude     = latitude
        self.__longitude    = longitude

    def get_nome(self) -> str:
        return self.__nome.get_value()

    def get_status_voo(self) -> str:
        return self.__status_voo.get_value()

    def get_bateria(self):
        # Protege contra None antes de chamar get_value() — bateria pode não ter sido informada
        return self.__bateria.get_value() if self.__bateria else None

    def to_dict(self) -> dict:
        """Serializa para resposta HTTP — inclui todos os campos operacionais."""
        return {
            'id':           self.__id,
            'operacao_id':  self.__operacao_id,
            'nome':         self.get_nome(),
            'status_voo':   self.get_status_voo(),
            'bateria':      self.get_bateria(),
            'conectividade': self.__conectividade,
            'latitude':     self.__latitude,
            'longitude':    self.__longitude
        }

    def to_db(self) -> dict:
        """Serializa para o banco — extrai os primitivos dos Value Objects."""
        return {
            'id':           self.__id,
            'operacao_id':  self.__operacao_id,
            'nome':         self.__nome.get_value(),
            'status_voo':   self.__status_voo.get_value(),
            # Guarda None explicitamente caso a bateria não tenha sido informada
            'bateria':      self.__bateria.get_value() if self.__bateria else None,
            'conectividade': self.__conectividade,
            'latitude':     self.__latitude,
            'longitude':    self.__longitude
        }
```

---

## Scans — `scan_entity.py`

---

### Value Objects

```python title="app/entities/scan_entity.py"
class ScanPlaca:
    def __init__(self, value: str):
        # Valor já normalizado (uppercase) pelo Service antes de chegar aqui
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class ScanStatusValidacao:
    # Representa o estado da decisão humana sobre o scan detectado pelo drone
    VALID = ['pendente', 'aprovado', 'rejeitado']

    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value
```

---

### Entidade `Scan`

```python title="app/entities/scan_entity.py"
class Scan:
    def __init__(self, id_drone: str, placa: ScanPlaca, match: bool,
                 status_validacao: ScanStatusValidacao = None,
                 imagem_url: str = None, latitude: float = None,
                 longitude: float = None, id: str = None):
        self.__id       = str(id) if id else str(uuid.uuid4())
        self.__id_drone = id_drone
        self.__placa    = placa
        self.__match    = match
        # Status padrão: 'pendente' — todo scan nasce aguardando revisão humana
        # O operador `or` garante o fallback caso status_validacao seja None explicitamente
        self.__status_validacao = status_validacao or ScanStatusValidacao('pendente')
        self.__imagem_url = imagem_url
        self.__latitude   = latitude
        self.__longitude  = longitude

    def get_placa(self) -> str:
        return self.__placa.get_value()

    def get_status(self) -> str:
        return self.__status_validacao.get_value()

    def is_match(self) -> bool:
        # Indica se o drone identificou correspondência com um veículo procurado
        return self.__match

    def to_dict(self) -> dict:
        """Serializa o scan completo para resposta HTTP, incluindo o status de validação."""
        return {
            'id':               self.__id,
            'id_drone':         self.__id_drone,
            'placa':            self.get_placa(),
            'match':            self.__match,
            'status_validacao': self.get_status(),
            'imagem_url':       self.__imagem_url,
            'latitude':         self.__latitude,
            'longitude':        self.__longitude
        }

    def to_db(self) -> dict:
        """Serializa para o INSERT — o status_validacao não é incluído aqui
        pois é gerenciado por update_validacao no Model, separadamente."""
        return {
            'id':        self.__id,
            'id_drone':  self.__id_drone,
            'placa':     self.__placa.get_value(),
            'match':     self.__match,
            'imagem_url': self.__imagem_url,
            'latitude':  self.__latitude,
            'longitude': self.__longitude
        }
```

**Detalhe importante:** `to_db()` não inclui `status_validacao` — o status inicial `pendente` é definido por `DEFAULT` no schema SQL, e as transições de estado são feitas por um `UPDATE` separado (`ScanModel.update_validacao`).

---

## Veículos — `veiculo_entity.py`

---

### Value Objects

```python title="app/entities/veiculo_entity.py"
class VeiculoPlaca:
    def __init__(self, value: str):
        # Valor já em maiúsculas — normalizado pelo Service antes da instanciação
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class VeiculoModelo:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value


class VeiculoCor:
    def __init__(self, value: str):
        self.__value = value

    def get_value(self) -> str:
        return self.__value
```

---

### Entidade `Veiculo`

```python title="app/entities/veiculo_entity.py"
class Veiculo:
    def __init__(self, placa: VeiculoPlaca, modelo: VeiculoModelo,
                 cor: VeiculoCor, roubado: bool, data_roubo: str, id: str = None):
        import uuid
        # UUID gerado no Python — independente do banco
        self.__id         = str(id) if id else str(uuid.uuid4())
        self.__placa      = placa
        self.__modelo     = modelo
        self.__cor        = cor
        # roubado é um booleano direto — não precisa de Value Object para tipo primitivo simples
        self.__roubado    = roubado
        self.__data_roubo = data_roubo

    def get_id(self) -> str:
        return self.__id

    def to_dict(self) -> dict:
        """Serializa para resposta HTTP — data_roubo convertida para string para compatibilidade JSON."""
        return {
            'id':         self.__id,
            'placa':      self.__placa.get_value(),
            'modelo':     self.__modelo.get_value(),
            'cor':        self.__cor.get_value(),
            'roubado':    self.__roubado,
            # Converte datetime para string caso a data venha como objeto Python
            'data_roubo': str(self.__data_roubo) if self.__data_roubo else None
        }

    def to_db(self) -> dict:
        """Serializa para persistência — o psycopg2 aceita o tipo datetime nativo."""
        return {
            'id':         self.__id,
            'placa':      self.__placa.get_value(),
            'modelo':     self.__modelo.get_value(),
            'cor':        self.__cor.get_value(),
            'roubado':    self.__roubado,
            # Mantém o tipo original para o banco interpretar corretamente (DATE/TIMESTAMP)
            'data_roubo': self.__data_roubo
        }
```
