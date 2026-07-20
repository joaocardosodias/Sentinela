---
sidebar_position: 5
title: Integração do Pipeline do Drone
---

# Documentação da Sprint — Integração do Pipeline do Drone

O sistema é composto por quatro serviços que rodam em paralelo:

| Serviço | Papel | Tecnologia |
|---|---|---|
| **backend** | API REST (autenticação, scans, veículos, operações) | Flask + PostgreSQL |
| **frontend** | Interface do operador (mapa, telemetria, validação de scans) | React + Vite |
| **drone_webrtc_server** | Captura de vídeo do Tello, transmissão WebRTC e detecção de placas (YOLO + OCR) | aiortc + ultralytics + easyocr |
| **supabase_matcher** | Worker que consome as detecções, consulta a API da Pier e grava os scans | psycopg2 + API Pier |

O fluxo de dados pretendido é:

```
Drone Tello → detecção (YOLO/OCR) → fila local (SQLite) → consulta Pier → tabela scans (Postgres)
```

---

## 2. Ponto de partida e diagnóstico inicial

Ao iniciar a sprint, o backend e o frontend já subiam, mas o fluxo do drone estava interrompido. O diagnóstico revelou três lacunas no código recebido:

1. **Ausência do ponto de entrada do pipeline.** Os módulos `supabase_matcher.py` e `sync_pending.py` estavam marcados como **depreciados** (lançavam `RuntimeError` ao serem executados) e apontavam para um arquivo central, `drone_pipeline.py`, que **não estava presente no projeto** — restava apenas o seu bytecode compilado (`.pyc`). Esse arquivo era descrito no próprio código como o "único ponto de entrada do sistema", além de todo o resto não funcionar por estar com o código desatualizado.

### Por que isso importa

Como o `drone_pipeline.py` estava com o código novo, o sistema só tinha **metade** do fluxo: o servidor do drone conseguia detectar e salvar localmente, mas nada consumia essa fila para comparar com a Pier e gravar os scans. Foi essa lacuna que a sprint precisou reconstruir.

---

## 3. O que foi feito

### 3.1. Reconstrução das dependências (`requirements.txt`)

**O quê:** geração de um `requirements.txt` a partir da análise dos imports reais do código.

**Por quê:** permitir que qualquer integrante (ou avaliador) recrie o ambiente Python com um único `pip install -r requirements.txt`, sem depender de conhecimento tácito sobre quais bibliotecas instalar.

### 3.2. Execução correta dos módulos (imports e `PYTHONPATH`)

**O quê:** padronização da forma de executar os módulos do drone, rodando a partir da pasta `src/` com a raiz do projeto no `PYTHONPATH`.

**Por quê:** o código foi escrito assumindo que o Python seria iniciado a partir da raiz do repositório, tratando `src` como um pacote (imports do tipo `from src.visao_computacional...`). Executar de dentro de uma subpasta gerava erros como `ModuleNotFoundError: No module named 'src'`. Rodar de `src/` com `PYTHONPATH` apontando para a raiz resolve a resolução de imports sem precisar reescrever cada arquivo.

### 3.3. Recuperação das constantes de controle de voo

**O quê:** definição das constantes de configuração do Tello que estavam sendo usadas mas não declaradas no `drone_webrtc_server.py` (timeout de comando, distância de movimento, graus de rotação, velocidade máxima e watchdog).

**Por quê:** o arquivo recebido referenciava essas constantes mas não as definia, causando `NameError` e impedindo o servidor de iniciar. Os valores foram definidos de forma conservadora e segura para o Tello, além de configuráveis via `.env`.

### 3.4. Reativação e correção do worker de sincronização (`supabase_matcher.py`)

Esta foi a mudança central da sprint. O arquivo `supabase_matcher.py` continha toda a lógica necessária (autenticação na Pier, consulta de placa, criação do scan no Postgres, limpeza da fila local), mas estava inutilizável. Três correções foram aplicadas:

**a) Remoção do bloqueio de depreciação.**
Removido o `RuntimeError` do topo, que impedia qualquer execução. *Por quê:* como o `drone_pipeline.py` que o substituiria não existia mais no projeto, o `supabase_matcher.py` precisou voltar a ser o responsável pela sincronização.

**b) Correção do import de `local_detections`.**
O import estava no formato "solto" (`from local_detections import ...`), que falhava fora da pasta `database/`. Foi trocado por um import resiliente (tenta `from database.local_detections` e, se falhar, recorre a `from local_detections`). *Por quê:* garante que o módulo funcione tanto executado como pacote quanto isoladamente.

**c) Integração de um worker automático em loop.**
Adicionada a função `run_sync_loop()` e um bloco `if __name__ == "__main__"`, que executam a sincronização em intervalos regulares (configuráveis via `SYNC_INTERVAL_SECONDS` e `SYNC_BATCH_LIMIT`).
*Por quê:* o arquivo original apenas **definia** funções — nada as chamava. Sem um laço de execução, "tirar o bloqueio" não produzia nenhum efeito. O loop transforma o módulo em um worker que drena a fila continuamente, em tempo real, **sem acionamento manual** — recriando o comportamento que o `drone_pipeline.py` tinha.

### 3.5. Correção do estado travado das detecções

**O quê:** procedimento para reverter detecções marcadas como `error` de volta para `pending`.

**Por quê:** quando uma sincronização falha, o código marca a detecção como `error`, e nada a reverte automaticamente. Como o worker só busca registros `pending`, todas as detecções das primeiras tentativas (feitas antes das correções) ficaram permanentemente ignoradas — dando a falsa impressão de que o sistema não fazia nada, quando na verdade a fila parecia vazia para ele. Reverter para `pending` permitiu reprocessá-las.

### 3.6. Correção do diretório dos frames (último elo até o frontend)

**O quê:** alinhamento do diretório onde o `supabase_matcher` **salva** os frames com o diretório de onde o backend os **serve**.

**Por quê:** o worker salvava os frames em `src/database/uploaded_frames/`, mas o backend procurava por eles em `g03/uploaded_frames/` (a raiz do projeto). Como os caminhos não coincidiam, o backend retornava **404** e a imagem aparecia quebrada no frontend. A correção ancorou o diretório de saída do worker na raiz do projeto, fazendo os dois lados apontarem para a mesma pasta. Esse foi o ajuste que fechou o fluxo visual: agora, quando há match, o frame capturado aparece corretamente nas telas de validação.

### 3.7. Scripts de inicialização (`.sh`)

**O quê:** criação de scripts shell para subir os serviços com um único comando, com encerramento limpo de todos os processos via `Ctrl+C`.

**Por quê:** o sistema exige múltiplos processos simultâneos, cada um com seu diretório de trabalho e variáveis de ambiente específicas. Subir tudo manualmente era trabalhoso e propenso a erros (esquecer um serviço, deixar processos órfãos segurando portas). Os scripts automatizam isso. Dois cuidados foram incorporados:

- **Encerramento por grupo de processos:** garante que processos-filho (como o Vite, iniciado pelo `npm run dev`) sejam encerrados junto com o pai, evitando portas presas ("porta em uso") na próxima execução.
- **Logs prefixados por origem** (`[backend]`, `[frontend]`, `[drone]`, `[sync]`): no script unificado, permite distinguir a origem de cada linha mesmo com os quatro serviços escrevendo no mesmo terminal.

---

## 4. Resultado final

Ao término da sprint, o fluxo funciona de ponta a ponta e de forma automática:

1. O drone captura vídeo e o transmite ao frontend via WebRTC.
2. O YOLO detecta placas e o OCR as transcreve, salvando cada detecção na fila local (SQLite).
3. O worker, em loop, autentica na Pier, consulta cada placa e grava o resultado na tabela `scans` do PostgreSQL.
4. Quando há match, o frame capturado é salvo e servido pelo backend, aparecendo nas telas de validação do frontend.

Todo o processo é iniciado por um único script e roda sem intervenção manual.

---

## 5. Como Rodar o Projeto?

Como juntamos todos os 4 arquivos responsáveis por fazer rodar o projeto, com apenas um comando podemos fazer isso: 

```bash
./start.sh
```