---
sidebar_position: 1
title: "Modularização e remoção do drone_pipeline.py"
---

# Modularização e remoção do `drone_pipeline.py`

## Resumo executivo

O arquivo `src/drone_pipeline.py` era um **monólito** de ~1080 linhas que concentrava, sozinho,
**todas** as camadas do sistema do drone: logging colorido no terminal, configuração de rede,
servidor WebRTC + telemetria, reconhecimento de placas com YOLO/OCR, fila local em SQLite, consulta
à API da Pier e sincronização com o Supabase.

Ao longo das sprints, o time foi **extraindo** cada uma dessas responsabilidades para módulos
menores e independentes na mesma pasta `src/`. Esta página documenta:

1. **o que** havia dentro do monólito e **para onde** cada parte foi;
2. **por que** o monólito era frágil;
3. a **última lacuna** que ainda dependia dele (o "produtor" da fila SQLite) e **como ela foi
   migrada**;
4. **todas** as mudanças de código aplicadas nesta refatoração;
5. **por que** foi seguro deletar o arquivo no fim.

> **Resultado:** `drone_pipeline.py` foi **removido**. Seu papel de runtime (transmitir vídeo ao
> dashboard **e** alimentar a fila de detecções) passou a ser feito pelo
> [`drone_webrtc_server.py`](https://github.com/) reutilizando os módulos extraídos, e a
> sincronização virou um script separado (`sync_pending.py`), coerente com o desenho offline-first
> do projeto.

---

## 1. O que era o `drone_pipeline.py`

Era um único processo que fazia, de uma só vez:

- **Logging colorido** — funções `_banner` / `log_*` que imprimiam linhas formatadas com cores ANSI.
- **Rede do Tello** — leitura da configuração e bind dos sockets UDP.
- **Servidor WebRTC + telemetria** — endpoints `POST /offer` e `WS /telemetry` (aiohttp/aiortc),
  além da thread de estado (UDP 8890) e do envio de comandos SDK (UDP 8889).
- **Captura + YOLO/OCR** — a classe `TelloVideoTrack` lia o stream H.264 (UDP 11111), rodava o
  reconhecimento de placas a cada N frames e **gravava** as placas válidas no SQLite.
- **Fila local SQLite** — criação da tabela `plate_frames` e operações de inserir/ler/atualizar/deletar.
- **API da Pier** — autenticação e consulta de placas.
- **Sincronização com o Supabase** — salvar o frame em disco e criar o `scan`, dentro de um
  **worker daemon** que rodava num loop infinito.

Ou seja: rede + vídeo + machine learning + banco local + API externa + banco na nuvem, **tudo no
mesmo arquivo**.

---

## 2. Por que o monólito era frágil

| Problema | Consequência |
|---|---|
| **Viola a responsabilidade única** | Um mesmo arquivo cuidava de rede, vídeo, ML, SQLite, Pier e Supabase. Qualquer mudança em uma camada arriscava quebrar as outras. |
| **Acoplamento forte / import pesado** | O topo do arquivo importava `aiortc`, `cv2`, `psycopg2`, `numpy`, `aiohttp` e o modelo YOLO de uma vez. Se **um** desses imports falhasse (ex.: máquina sem `psycopg2`), **nada** rodava — nem o vídeo simples. |
| **Configuração duplicada e divergente** | URLs da Pier, caminho do SQLite, IDs do drone e config de rede ficavam fixos no monólito **e** repetidos nos módulos novos. Os valores já tinham divergido: o monólito usava `DEFAULT_DRONE_ID` *fixo no código*, enquanto o [`supabase_matcher.py`](https://github.com/) lê do `.env` com *fallback* mockado. |
| **Efeitos colaterais no import** | Já no import o arquivo executava `load_dotenv()` e fazia `raise RuntimeError` se faltasse `DATABASE_URL`. Isso torna o módulo **impossível de importar para teste** sem um ambiente completo. |
| **Fundia captura offline e sync online** | O desenho do projeto (ver [Avanços da YOLO e Conexão com a API da Pier](../../sprint-3/Backend/yolo_banco.md)) separa **coleta offline** (durante o voo, sem internet) de **sincronização online** (depois, com internet). O monólito juntava as duas num só processo, com uma thread de sync rodando o tempo todo — contrariando esse desenho. |

---

## 3. Para onde cada parte foi (mapa da extração)

| Responsabilidade no monólito | Módulo que assumiu |
|---|---|
| Config de rede / socket Tello (`load_tello_config`, `bind_tello_socket`, `describe_network_plan`) | [`src/network_routes.py`](https://github.com/) |
| WebRTC `/offer` + `/telemetry` + envio de comando + thread de estado + streaming de vídeo | [`src/drone_webrtc_server.py`](https://github.com/) |
| SQLite — ler / atualizar / deletar | [`src/local_detections.py`](https://github.com/) |
| API da Pier + Supabase + criação de `scan` + loop de sync | [`src/supabase_matcher.py`](https://github.com/) |
| Entry point da sincronização | [`src/sync_pending.py`](https://github.com/) |
| Reconhecimento de placas (`process_frame`) | [`src/visao_computacional/yolo26/plate_recognizer.py`](https://github.com/) |
| Logging colorido (`COLOR` / `_banner` / `log_*`) | **descartado** — os módulos usam `logging`/`print` simples |
| **Produtor da fila SQLite (gravar a detecção ao vivo)** | **migrado nesta refatoração** → `local_detections.py` + `drone_webrtc_server.py` |

---

## 4. A lacuna encontrada antes de deletar

Antes de remover o arquivo foi feita uma **análise de lacunas**: existia algum trecho que só
existia no `drone_pipeline.py`? A resposta foi **sim**, em um ponto importante.

O `drone_pipeline.py` era o **único "produtor" ao vivo** da fila SQLite no caminho do modelo
**yolo26** (o usado em voo). Reparando nos outros arquivos:

- O `drone_webrtc_server.py` **transmitia** o vídeo, mas **não detectava nem gravava** nada.
- O `drone.py` **detectava** ao vivo, mas só **exibia** numa janela local (não persistia).
- O `local_detections.py` só **lia / atualizava / deletava** — não **inseria**.
- A gravação completa (criar tabela + inserir) existia em `yolo11/plate_recognizer.py`, mas só no
  caminho **yolo11** (processando arquivo de vídeo), **não** no runtime yolo26 ao vivo.

Ou seja: se simplesmente apagássemos o `drone_pipeline.py`, **ninguém mais alimentaria** a fila
`plate_frames` que todo o pipeline de sincronização (`local_detections` → `supabase_matcher` →
`sync_pending`) consome. Por isso, o produtor foi **migrado primeiro** e só depois o arquivo foi
deletado.

---

## 5. Mudanças de código aplicadas nesta refatoração

Esta seção registra **tudo** o que foi alterado no código.

### 5.1 `src/local_detections.py` — consolidar o DAO do SQLite

O módulo só tinha leitura/atualização/exclusão. Foram adicionadas as funções de **escrita**, para
ele se tornar o **dono único** da fila local (cria a tabela e insere a detecção). Isso espelha o que
o monólito fazia em `_ensure_table` / `_save_detection_local`.

**Adicionado:** import de `cv2` e `datetime`, a constante `JPEG_QUALITY` e as funções abaixo.

```python
def ensure_table():
    """
    Cria a tabela plate_frames se ela ainda não existir.
    Esquema único da fila local: produtor e consumidor dependem destas colunas.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plate_frames (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            plate        TEXT    NOT NULL,
            plate_format TEXT,
            confidence   REAL,
            bbox         TEXT,
            frame_blob   BLOB,
            status       TEXT    NOT NULL DEFAULT 'pending',
            created_at   TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_detection(plate, plate_format, confidence, bbox, frame_bgr):
    """
    Persiste uma detecção válida com status='pending'.
    Codifica o frame (BGR) como JPEG e guarda como BLOB. Retorna o id, ou None.
    """
    ok, buffer = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    frame_blob = buffer.tobytes() if ok else None

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO plate_frames (
            plate, plate_format, confidence, bbox, frame_blob, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    """, (
        plate, plate_format, float(confidence),
        json.dumps(bbox), frame_blob, datetime.now().isoformat(),
    ))
    detection_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return detection_id
```

**Por quê:** com isso, **todo** acesso ao SQLite passa por um único módulo (criar, inserir, ler,
atualizar, deletar), eliminando a duplicação que existia no monólito e no `yolo11`.

### 5.2 `src/drone_webrtc_server.py` — tornar o servidor o "produtor"

O `TelloVideoTrack` deste servidor só transmitia vídeo. Agora ele também roda YOLO/OCR de forma
assíncrona e grava as placas válidas na fila — exatamente o papel que o monólito tinha, mas
**reutilizando** os módulos extraídos em vez de duplicar código.

**a) Imports adicionados** (mesmo padrão `try/except` relativo→absoluto já usado para `network_routes`):

```python
try:
    from .local_detections import SQLITE_DB_PATH, ensure_table, save_detection
except ImportError:
    from local_detections import SQLITE_DB_PATH, ensure_table, save_detection
```

**b) Constantes de throttle** (no nível do módulo) — controlam a frequência da detecção sem travar
o vídeo:

```python
YOLO_EVERY_N_FRAMES = 3
MIN_SECONDS_BETWEEN_DETECTIONS = 0.25
```

**c) Helpers de reconhecimento + gravação** (import do YOLO é **lazy**, para não carregar o modelo
no import do módulo):

```python
def _run_plate_recognition(frame):
    try:
        from src.visao_computacional.yolo26.plate_recognizer import process_frame
    except ModuleNotFoundError:
        from visao_computacional.yolo26.plate_recognizer import process_frame
    _, results = process_frame(frame)
    return results


def _save_valid_detections(results, frame):
    for r in results:
        if not r.get("valid") or not r.get("plate"):
            continue
        save_detection(
            plate=r["plate"],
            plate_format=r.get("format", "UNKNOWN"),
            confidence=r.get("confidence", 0.0),
            bbox=r.get("bbox", []),
            frame_bgr=frame,
        )
        logger.info("Detecção salva na fila local: %s", r["plate"])
```

**d) `TelloVideoTrack.__init__`** — o pool subiu de 1 para **2 workers** (um para a leitura
bloqueante do frame, outro para o YOLO) e foram adicionados os campos de estado da detecção:

```python
# antes: self._executor = ThreadPoolExecutor(max_workers=1)
self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
self._frame_count = 0
self._next_processing_at = 0.0
self._processing_future = None
```

**e) `TelloVideoTrack.recv`** — depois de ler o frame, dispara a detecção assíncrona quando a janela
de throttle permite. A cópia do frame é capturada no *closure* para a thread não ver o buffer
sobrescrito por frames futuros. O frame enviado por WebRTC **continua sem overlay** — a gravação é
um efeito colateral:

```python
if should_detect:
    def _make_task(frame_copy):
        def _task():
            results = _run_plate_recognition(frame_copy)
            _save_valid_detections(results, frame_copy)
            return results
        return _task

    self._processing_future = loop.run_in_executor(
        self._executor, _make_task(bgr_frame.copy())
    )
    self._processing_future.add_done_callback(self._on_detection_done)
    self._next_processing_at = now + MIN_SECONDS_BETWEEN_DETECTIONS
```

Também foi adicionado o callback `_on_detection_done`, que registra erros do YOLO e libera o slot de
processamento.

**f) `main()`** — garante a existência da tabela no startup, como o monólito fazia:

```python
ensure_table()
logger.info("Banco local pronto: %s", SQLITE_DB_PATH)
```

### 5.3 `src/drone_pipeline.py` — removido

O arquivo foi **deletado**. Tudo o que ele fazia passou a viver nos módulos da tabela da
[seção 3](#3-para-onde-cada-parte-foi-mapa-da-extração). O único log colorido (`_banner`/`log_*`)
foi descartado por ser apenas estética de terminal do antigo demo monolítico.

---

## 6. Por que deletar ficou seguro

- **Nenhum arquivo importava `drone_pipeline`** — uma busca global no projeto encontrou apenas
  auto-referências dentro do próprio arquivo. Logo, remover não quebra nenhum `import`.
- **A última dependência real (o produtor da fila) foi migrada** para o `drone_webrtc_server.py` +
  `local_detections.py` antes da remoção.
- O **daemon de sync em processo** do monólito já estava coberto pelo `sync_pending.py` /
  `process_pending_detections` — agora rodado **sob demanda** (quando há internet), exatamente como
  o desenho offline-first pede.

---

## 7. Como o fluxo roda hoje

```text
[ Voo / offline ]                                  [ Com internet ]
drone_webrtc_server.py                              sync_pending.py
  ├─ stream WebRTC  ─────────────►  dashboard         └─ process_pending_detections()
  └─ YOLO (yolo26) ─► save_detection()                     ├─ get_pending_detections()  (local_detections)
                          │                                ├─ consulta API da Pier      (supabase_matcher)
                          ▼                                ├─ se match: salva frame + cria scan no Supabase
                   SQLite: plate_frames  ◄────────────────┘   └─ delete/update do registro local
                   (fila 'pending')
```

- **Produtor:** `drone_webrtc_server.py` grava as placas válidas em `plate_frames` (status `pending`).
- **Fila:** SQLite local (`local_detections.db`), resiliente a falta de internet durante o voo.
- **Consumidor:** `sync_pending.py` → `supabase_matcher.py` consulta a Pier e cria os `scans` no
  Supabase, removendo/atualizando os registros locais.

---

## 8. Como verificar

1. **DAO (SQLite):** chamar `ensure_table()`, depois
   `save_detection("ABC1D23", "Mercosul", 0.9, [0,0,10,10], frame)` e conferir que
   `get_pending_detections()` retorna a linha; `delete_local_detection(id)` limpa.
2. **Runtime:** rodar `python -m src.drone_webrtc_server` com o drone transmitindo. Ao detectar uma
   placa válida, uma nova linha aparece em `plate_frames` com status `pending`. Sem drone, ao menos
   o import do módulo e o `ensure_table()` (que cria o `.db`) devem rodar sem erro.
3. **Sincronização ponta-a-ponta** (precisa de credenciais Pier/Supabase no `.env`):
   `python -m src.sync_pending` consome os pendentes e cria os `scans`.
