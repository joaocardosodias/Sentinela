---
sidebar_position: 1
title: TUI - Terminal User Interface
---

# Integração da API da Pier no sincronizador de detecções

## 1. Objetivo da tarefa

O objetivo desta alteração foi substituir a comparação local de placas realizada diretamente contra a tabela `veiculos` do Supabase/PostgreSQL por uma consulta à API da Pier.

A mudança foi feita de forma cirúrgica: toda a lógica nova foi concentrada no arquivo:

```text
src/supabase_matcher.py
```

Nenhuma alteração foi realizada nos módulos de detecção de imagem, OCR, captura do drone, SQLite local, front-end ou scripts externos de sincronização.

---

## 2. Contexto do projeto

O projeto possui um fluxo em que o drone envia frames de vídeo para o módulo de visão computacional. A YOLO identifica a região da placa e o OCR extrai seus caracteres. A detecção é armazenada temporariamente em um SQLite local para ser processada posteriormente.

O fluxo simplificado é:

```text
Drone
  ↓
Vídeo
  ↓
YOLO detecta a placa
  ↓
OCR lê os caracteres
  ↓
SQLite local armazena a detecção como pending
  ↓
Sincronizador processa os registros pendentes
  ↓
Supabase/PostgreSQL recebe os scans processados
```

Antes desta alteração, o sincronizador usava a tabela `veiculos` do Supabase como fonte para decidir se uma placa possuía match.

---

## 3. Problema original

A regra anterior estava implementada dentro de `supabase_matcher.py` de forma semelhante a:

```python
veiculo = find_veiculo_by_plate(cursor, plate)
has_match = veiculo is not None
```

Ou seja, o sincronizador:

1. abria uma conexão com o Supabase/PostgreSQL;
2. consultava a tabela `veiculos`;
3. verificava se a placa existia localmente;
4. definia `match=True` ou `match=False` com base nessa busca.

Esse comportamento precisava ser substituído porque a fonte oficial da comparação passou a ser a API da Pier.

---

## 4. Escopo definido

A decisão foi alterar somente o arquivo `src/supabase_matcher.py`.

### Foi alterado

- autenticação na API da Pier;
- consulta de placas na API da Pier;
- interpretação do resultado retornado;
- renovação do token em caso de `401 Unauthorized`;
- tratamento de erros técnicos;
- origem da decisão de `has_match`.

### Não foi alterado

- YOLO;
- OCR;
- captura do drone;
- forma como o SQLite armazena detecções pendentes;
- estrutura da tabela `scans`;
- salvamento local de frames com match;
- exclusão do registro temporário do SQLite após processamento bem-sucedido;
- front-end;
- arquivo `sync_pending.py`;
- arquivo de teste isolado `query_inteli_api.py`.

A escolha de concentrar tudo em um único arquivo reduz o impacto da mudança e facilita reversão, testes e revisão de código.

---

## 5. Novo fluxo implementado

Após a alteração, o sincronizador funciona assim:

```text
SQLite local
  ↓
Busca detecções com status pending
  ↓
Autentica uma vez na API da Pier
  ↓
Recebe access_token temporário
  ↓
Para cada placa pendente:
  ↓
Normaliza a placa
  ↓
Consulta POST /v1/inteli/vehicle-lookups
  ↓
Interpreta a resposta da Pier
  ├── status == "found" → match=True
  ├── HTTP 404 → match=False
  └── erro técnico → marca detecção como error
  ↓
Se match=True, salva o frame localmente
  ↓
Cria registro na tabela scans
  ↓
Exclui a detecção temporária do SQLite
```

---

## 6. Endpoints utilizados

### Autenticação

```text
POST https://auth.stag.pier.zone/realms/pier-ext-auth-apis/protocol/openid-connect/token
```

A autenticação utiliza o formato:

```text
Content-Type: application/x-www-form-urlencoded
```

Com os campos:

```text
grant_type=password
username=<usuário do grupo>
password=<senha do grupo>
client_id=pier-ext-auth-apis-client
client_secret=<segredo da aplicação>
```

A API retorna um `access_token` temporário, que é usado nas consultas seguintes.

### Consulta de placa

```text
POST https://gw2.stag.pier.zone/v1/inteli/vehicle-lookups
```

Headers:

```text
Authorization: Bearer <access_token>
Content-Type: application/json
```

Payload enviado:

```json
{
  "license_plate": "MJF4A91",
  "geolocation": {
    "latitude": -23.5505,
    "longitude": -46.6333
  }
}
```

---

## 7. Funções adicionadas ao `supabase_matcher.py`

### `validate_pier_configuration()`

Responsável por verificar se as credenciais obrigatórias da Pier foram definidas no `.env`.

Variáveis validadas:

```text
PIER_USERNAME
PIER_PASSWORD
PIER_CLIENT_SECRET
```

Caso alguma esteja ausente, o sincronizador interrompe o processamento antes de consultar placas.

### `get_pier_access_token()`

Responsável por:

1. validar as configurações;
2. montar o payload de autenticação;
3. enviar a requisição ao endpoint de token;
4. interpretar o JSON retornado;
5. devolver o `access_token`.

A autenticação é realizada uma vez no início de cada execução do sincronizador, evitando gerar um token novo para cada placa.

### `lookup_vehicle_on_pier(access_token, plate)`

Responsável por:

1. normalizar a placa;
2. montar o payload com placa e geolocalização;
3. enviar a requisição de consulta;
4. interpretar a resposta da Pier;
5. distinguir placa não encontrada de falha técnica.

### `pier_result_has_match(pier_result)`

Responsável por transformar a resposta da Pier em uma decisão booleana:

```python
return str(pier_result.get("status", "")).lower() == "found"
```

Assim, o sistema considera como match somente uma resposta que contenha:

```json
{
  "status": "found"
}
```

### `PierApiError`

Foi criada uma exceção específica para erros técnicos relacionados à Pier:

```python
class PierApiError(RuntimeError):
    ...
```

Ela permite separar problemas de infraestrutura de resultados legítimos de comparação.

---

## 8. Decisões técnicas adotadas

### 8.1. Toda a lógica ficou em um único arquivo

A integração foi incorporada diretamente ao `supabase_matcher.py`.

**Motivo:** o objetivo era realizar apenas a troca da fonte de comparação, sem criar novas dependências entre módulos nem ampliar o escopo da alteração.

### 8.2. Credenciais ficam no `.env`

As credenciais da Pier não foram mantidas escritas diretamente no código.

Exemplo de configuração:

```env
PIER_USERNAME=<usuario>
PIER_PASSWORD=<senha>
PIER_CLIENT_ID=pier-ext-auth-apis-client
PIER_CLIENT_SECRET=<client_secret>
```

**Motivo:** credenciais embutidas no código podem vazar em commits, compartilhamentos de arquivo ou repositórios públicos.

### 8.3. Token gerado uma vez por execução

O token é obtido antes do loop que percorre as detecções pendentes.

**Motivo:** reduzir chamadas desnecessárias ao endpoint de autenticação e evitar overhead para cada placa processada.

### 8.4. Renovação automática do token em caso de `401`

Caso a consulta de uma placa receba `401 Unauthorized`, o código:

1. gera um novo token;
2. repete somente a consulta atual;
3. segue o fluxo normalmente se a nova tentativa funcionar.

**Motivo:** o token da Pier é temporário. Como um lote pode demorar para ser processado, o token pode expirar no meio da sincronização.

### 8.5. `404` é tratado como ausência de match

Quando a Pier devolve `404`, a função converte a resposta para:

```python
{
    "status": "not_found",
    "message": "Vehicle not found",
}
```

**Motivo:** placa não encontrada é um resultado válido da comparação, e não uma falha técnica.

### 8.6. Erros técnicos não viram falsos negativos

Erros como:

```text
401 após nova tentativa
500
falha de conexão
timeout
JSON inválido
credencial ausente
```

não são interpretados como `match=False`.

Nesses casos, a detecção local é marcada como:

```text
error
```

**Motivo:** se a API estiver indisponível, assumir `match=False` poderia descartar ou classificar incorretamente uma placa relevante.

### 8.7. Normalização da placa antes da consulta

A placa é convertida para letras maiúsculas e recebe apenas caracteres alfanuméricos:

```python
return re.sub(r"[^A-Z0-9]", "", plate.upper())
```

Exemplo:

```text
bra-2e19 → BRA2E19
```

**Motivo:** padronizar o formato enviado à Pier e reduzir falhas causadas por hífens, espaços ou caracteres extras provenientes do OCR.

### 8.8. Geolocalização configurável

Latitude e longitude possuem valores padrão, mas podem ser sobrescritas pelo `.env`:

```env
PIER_LATITUDE=-23.5505
PIER_LONGITUDE=-46.6333
```

**Motivo:** manter compatibilidade com o mock atual e permitir ajustes futuros sem alterar o código.

### 8.9. Timeout configurável

As chamadas à Pier possuem limite de espera configurável:

```env
PIER_TIMEOUT_SECONDS=10
```

**Motivo:** impedir que uma indisponibilidade externa bloqueie o sincronizador indefinidamente.

---

## 9. Comportamento preservado no Supabase

A forma como os scans são gravados foi preservada.

### Quando há match

```text
match=True
imagem_url preenchida
frame salvo em uploaded_frames/<PLACA>/<timestamp>.jpg
scan criado no Supabase/PostgreSQL
registro removido do SQLite
```

### Quando não há match

```text
match=False
imagem_url=None
scan criado no Supabase/PostgreSQL
registro removido do SQLite
```

Essa decisão mantém o comportamento anterior do projeto. A única diferença é que a decisão de match passa a vir da Pier em vez da tabela `veiculos`.

> Observação: caso a regra de negócio mude para “sem match deve ser excluído sem criar scan”, será necessária uma pequena alteração adicional dentro de `process_pending_detections()`.

---

## 10. Comportamento em caso de erro

### Falha ao autenticar antes do processamento

Se a autenticação inicial falhar:

```text
nenhuma placa é processada
registros permanecem como pending
```

**Motivo:** permitir nova tentativa posteriormente sem perder a fila local.

### Falha técnica durante uma consulta

Se ocorrer erro técnico ao consultar uma placa específica:

```text
registro local recebe status error
scan não é criado
registro não é excluído do SQLite
```

**Motivo:** preservar o dado para análise ou tentativa futura.

### Token expirado durante o lote

Se ocorrer `401` durante uma consulta:

```text
novo token é gerado
consulta atual é repetida uma vez
```

---

## 11. Variáveis de ambiente necessárias

Adicionar ao arquivo `.env`:

```env
DATABASE_URL=<url_do_postgresql_ou_supabase>
DEFAULT_DRONE_ID=<uuid_do_drone>

PIER_USERNAME=<usuario_da_pier>
PIER_PASSWORD=<senha_da_pier>
PIER_CLIENT_ID=pier-ext-auth-apis-client
PIER_CLIENT_SECRET=<segredo_da_aplicacao>
```

Variáveis opcionais:

```env
PIER_LATITUDE=-23.5505
PIER_LONGITUDE=-46.6333
PIER_TIMEOUT_SECONDS=10
```

---

## 12. Arquivo alterado

Apenas este arquivo precisa ser substituído no projeto:

```text
src/supabase_matcher.py
```

O arquivo `query_inteli_api.py` pode continuar existindo como teste manual isolado, mas não é necessário para o fluxo principal.

---

## 13. Roteiro de validação

### 13.1. Verificar sintaxe

Dentro da pasta `src`, executar:

```bash
python3 -m py_compile supabase_matcher.py
```

Resultado esperado:

```text
nenhuma mensagem de erro
```

### 13.2. Configurar o `.env`

Confirmar que todas as variáveis obrigatórias estão preenchidas.

### 13.3. Executar o sincronizador

```bash
python3 sync_pending.py
```

### 13.4. Testar uma placa existente no mock

Exemplos fornecidos para teste:

```text
MJF4A91
BRA2E19
QWE1R23
JKL4M56
```

Resultado esperado no terminal:

```text
Match encontrado na Pier para <PLACA>. Scan criado com match=True e imagem_url preenchida.
```

### 13.5. Testar uma placa inexistente

Exemplo:

```text
ABC1D23
```

Resultado esperado:

```text
Sem match na Pier para ABC1D23. Scan criado com match=False e imagem_url=None.
```

### 13.6. Testar indisponibilidade da API

É possível simular falha removendo temporariamente uma credencial do `.env`.

Resultado esperado:

```text
Não foi possível iniciar a sincronização com a Pier: ...
```

Os registros devem permanecer como `pending`.

---

## 14. Pontos para evolução futura

Estas melhorias não fizeram parte da tarefa atual, mas podem ser avaliadas posteriormente:

1. utilizar o endpoint de confirmação da Pier após validação humana;
2. implementar retentativa automática para detecções marcadas como `error`;
3. registrar logs estruturados em arquivo ou serviço externo;
4. guardar o `vehicle_lookup_id` retornado pela Pier na tabela `scans`;
5. armazenar dados complementares retornados pela Pier, como marca, modelo, ano, cor e claims;
6. definir formalmente se qualquer `status="found"` representa alerta ou apenas existência no catálogo;
7. rotacionar credenciais que tenham sido compartilhadas em arquivos ou mensagens;
8. avaliar uso de refresh token para lotes maiores.

---

## 15. Resumo final

A tarefa substituiu a comparação local contra a tabela `veiculos` por uma consulta à API da Pier, mantendo intacto o restante do projeto.

A alteração foi concentrada exclusivamente em `src/supabase_matcher.py` e incluiu:

- autenticação via token;
- consulta de placa;
- normalização dos caracteres;
- decisão de match baseada em `status="found"`;
- tratamento de `404` como ausência legítima de match;
- renovação automática do token em caso de `401`;
- proteção contra falsos negativos em falhas técnicas;
- leitura segura de credenciais pelo `.env`;
- preservação do comportamento já existente de criação de scans e exclusão de detecções temporárias após sucesso.

