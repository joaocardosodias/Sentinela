---
sidebar_position: 2
title: Relatório de Testes
---

# Relatório de Testes

## 1. Revisão dos Requisitos

&emsp;Esta seção revisita os requisitos funcionais e não funcionais do sistema na sua versão vigente, consolidada na Sprint 2 a partir do feedback recebido na avaliação da Sprint 1. As alterações mais relevantes foram: remoção do requisito de GPS (RF-03 reescrito como Registro Temporal e de Zona de Operação), remoção do RNF-06 (precisão de georreferenciamento incompatível com o drone Tello), eliminação da redundância entre RNF-01 e RNF-02, e ajuste do limite de latência de alerta para 2 segundos. Os requisitos apresentados a seguir são os que orientam os testes descritos neste documento.

### 1.1 Requisitos Funcionais

| ID | Requisito | Descrição |
|----|-----------|-----------|
| RF-01 | Captura de Imagem | O sistema deve capturar imagens nítidas de placas de veículos estacionados e em movimento pela câmera do drone. |
| RF-02 | Visão Computacional | O sistema deve extrair os caracteres alfanuméricos das placas capturadas, utilizando visão computacional. |
| RF-03 | Registro Temporal e de Zona | O sistema deve associar automaticamente o horário (Date Time) e a zona de operação da missão ao registro de cada placa identificada. |
| RF-04 | Consulta de Sinistros | O sistema deve realizar chamada automática à API da Pier para verificar o status de roubo ou furto da placa capturada. |
| RF-05 | Notificação de Match | Caso a placa conste na base de sinistros, o sistema deve gerar alerta imediato com a placa, a zona de operação e o Date Time da detecção. |
| RF-06 | Health Check | O sistema deve garantir que os drones estão conectados e enviando dados da operação. |

### 1.2 Requisitos Não Funcionais

| ID | Requisito | Descrição | Meta |
|----|-----------|-----------|------|
| RNF-01 | Tempo de Resposta do Pipeline | O pipeline completo — da captura ao alerta — deve ser concluído em até 5 segundos. | ≤ 5 s |
| RNF-02 | Latência de Alerta Crítico | Uma vez detectado um match positivo, o alerta deve ser disparado para o frontend em menos de 2 segundos. | < 2 s |
| RNF-03 | Latência de Vídeo no Dashboard | O vídeo exibido no dashboard deve apresentar latência inferior a 5 segundos. | < 5 s |
| RNF-04 | Acurácia do Modelo | O modelo deve atingir acurácia mínima de 80% na leitura de placas em condições normais de operação. | ≥ 80% |
| RNF-05 | Health Check via Telemetria | A verificação de conectividade dos drones deve ser feita exclusivamente pelas informações de telemetria enviadas pelo drone. | — |

---

## 2. Planejamento dos Testes

&emsp;Os testes foram divididos em dois grupos com naturezas distintas. O primeiro grupo reúne os **testes que dependem de validação do usuário** — situações em que a avaliação envolve julgamento subjetivo do operador, como clareza visual, usabilidade de uma interface ou adequação de uma resposta operacional. O segundo grupo reúne os **testes objetivos de validação de métricas** — situações em que existe um critério de aceite mensurável e verificável de forma independente, como percentuais de acurácia, medições de latência ou verificação de registros no banco de dados.

&emsp;Essa separação é importante porque as estratégias de execução e de coleta de resultado são diferentes: os testes do primeiro grupo requerem sessões com usuários ou representantes do parceiro, enquanto os do segundo podem ser executados de forma automatizada ou com instrumentação direta no sistema.

&emsp;Além dos procedimentos manuais planejados (Seção 3), nesta sprint todos os testes receberam uma **versão automatizada equivalente**, executada contra o sistema real — os procedimentos adaptados, as tecnologias empregadas e os resultados obtidos estão documentados na Seção 4.

### 2.1 Testes com Validação do Usuário

| ID | Nome | Requisitos Cobertos |
|----|------|---------------------|
| TV-01 | Qualidade das Imagens Capturadas para Evidência | RF-01 |
| TV-02 | Usabilidade do Fluxo de Validação na Central de Alertas | RF-05 |
| TV-03 | Clareza do Monitoramento de Conectividade dos Drones | RF-06, RNF-05 |

### 2.2 Testes Objetivos de Validação de Métricas

| ID | Nome | Requisitos Cobertos |
|----|------|---------------------|
| TM-01 | Acurácia do Pipeline de Reconhecimento de Placas | RF-02, RNF-04 |
| TM-02 | Registro Temporal e de Zona de Operação | RF-03 |
| TM-03 | Consulta e Correspondência na Base de Sinistros | RF-04 |
| TM-04 | Latência Total do Pipeline End-to-End | RNF-01 |
| TM-05 | Latência de Disparo de Alerta Crítico | RNF-02 |
| TM-06 | Latência do Streaming de Vídeo no Dashboard | RNF-03 |
| TM-07 | Autenticação e Controle de Acesso da API | — (segurança transversal) |

---

## 3. Implementação dos Testes

### 3.1 Testes com Validação do Usuário

---

#### TV-01 — Qualidade das Imagens Capturadas para Evidência

**Requisito coberto:** RF-01

**Objetivo:** Verificar se as imagens geradas pelo pipeline e armazenadas como evidência são suficientemente nítidas para permitir a identificação visual da placa e do veículo por um operador humano.

**Pré-condições:**
- Pipeline de visão computacional em execução com o drone DJI Tello.
- Ao menos 10 imagens capturadas em condições distintas (distância, iluminação, ângulo).
- Imagens acessíveis via `imagem_url` na API ou localmente.

**Procedimento:**
1. Executar o pipeline com o drone em operação real ou em modo de teste com imagens estáticas.
2. Coletar as imagens armazenadas como evidência nos registros de scan.
3. Apresentar as imagens a pelo menos dois avaliadores (operador de campo e representante do parceiro).
4. Solicitar que cada avaliador classifique cada imagem como: _"adequada para evidência"_, _"aceitável com ressalvas"_ ou _"inadequada"_.

**Critério de aceite:** Ao menos 80% das imagens avaliadas classificadas como _"adequada"_ ou _"aceitável com ressalvas"_.

---

#### TV-02 — Usabilidade do Fluxo de Validação na Central de Alertas

**Requisito coberto:** RF-05

**Objetivo:** Verificar se um operador consegue, de forma intuitiva e sem treinamento prévio extenso, visualizar um alerta de match, avaliar as informações apresentadas e executar a ação de aprovação ou rejeição.

**Pré-condições:**
- Backend e frontend em execução com dados reais ou simulados de scans com `match = true` e `status_validacao = "pendente"`.
- Usuário autenticado com papel de `gestor_remoto` ou `gestor_local`.

**Procedimento:**
1. Apresentar o sistema a um avaliador que não participou do desenvolvimento.
2. Solicitar que o avaliador realize as seguintes tarefas sem orientação direta:
   - Acessar a Central de Alertas.
   - Localizar um alerta pendente.
   - Visualizar as informações do scan (placa, zona, data/hora, imagem).
   - Executar a ação de aprovação em um alerta e rejeição em outro.
3. Registrar o tempo necessário para completar cada tarefa e anotar dificuldades observadas.
4. Aplicar questionário de satisfação após a sessão (escala de 1 a 5).

**Critério de aceite:** Avaliador consegue completar o fluxo completo em até 3 minutos sem assistência, com nota média de satisfação ≥ 3,5.

---

#### TV-03 — Clareza do Monitoramento de Conectividade dos Drones

**Requisitos cobertos:** RF-06, RNF-05

**Objetivo:** Verificar se a interface de monitoramento comunica de forma clara o estado de conectividade dos drones, permitindo que o operador identifique rapidamente um drone desconectado ou com telemetria ausente.

**Pré-condições:**
- Tela de gerenciamento de operações (OperationsManager) em execução.
- Ao menos um drone registrado no sistema, com estado de conectividade variado (conectado e desconectado).

**Procedimento:**
1. Apresentar a tela de operações ao avaliador.
2. Simular a desconexão de um drone (interrompendo o envio de telemetria).
3. Solicitar que o avaliador identifique qual drone está desconectado apenas pela interface, sem informações externas.
4. Registrar o tempo até a identificação correta e eventuais dúvidas levantadas pelo avaliador.

**Critério de aceite:** Avaliador identifica corretamente o estado de conectividade dos drones em até 30 segundos, sem necessitar de explicação sobre a interface.

---

### 3.2 Testes Objetivos de Validação de Métricas

---

#### TM-01 — Acurácia do Pipeline de Reconhecimento de Placas

**Requisitos cobertos:** RF-02, RNF-04

**Objetivo:** Medir a taxa de acerto do pipeline YOLO + OCR na leitura de placas veiculares, verificando se atinge a meta de 80% definida no RNF-04.

**Pré-condições:**
- Pipeline de visão computacional configurado com o modelo YOLO26 e EasyOCR.
- Dataset de validação com ao menos 50 imagens de placas reais com ground truth conhecida.
- Imagens coletadas em condições variadas: frontal, leve inclinação, distâncias distintas.

**Procedimento:**
1. Executar o `plate_recognizer.py` sobre cada imagem do dataset via `cv2.imread` (modo de teste estático).
2. Comparar a placa retornada com o ground truth correspondente.
3. Registrar como _correto_ apenas leituras com correspondência exata da placa completa.
4. Calcular a acurácia: `acertos / total * 100`.
5. Repetir o teste com 10 imagens capturadas em tempo real com o drone para validação em ambiente real.

**Critério de aceite:** Acurácia ≥ 80% nos testes com imagens estáticas.

---

#### TM-02 — Registro Temporal e de Zona de Operação

**Requisito coberto:** RF-03

**Objetivo:** Verificar se cada scan registrado no banco de dados contém corretamente o timestamp de detecção e a zona de operação associada à missão em execução.

**Pré-condições:**
- Backend em execução com banco de dados configurado.
- Ao menos uma operação cadastrada no sistema com zona definida.
- Pipeline executando e enviando scans via `POST /api/scans/`.

**Procedimento:**
1. Iniciar uma operação com zona de operação definida.
2. Capturar ao menos 5 placas pelo pipeline durante a operação.
3. Consultar os registros no banco via `GET /api/scans/` ou diretamente no banco de dados.
4. Verificar, para cada scan: presença do campo `created_at` (timestamp), presença do campo de zona/operação associada, e coerência entre o horário do registro e o horário da captura.

**Critério de aceite:** 100% dos scans registrados possuem `created_at` preenchido e estão vinculados à operação ativa no momento da captura.

---

#### TM-03 — Consulta e Correspondência na Base de Sinistros

**Requisito coberto:** RF-04

**Objetivo:** Verificar se o sistema realiza a consulta automática à API da Pier (ou ao banco local de sinistros simulado) após a leitura de cada placa, retornando corretamente o status de match ou não match.

**Pré-condições:**
- `supabase_matcher.py` configurado com credenciais válidas ou banco local `local_detections.db` populado com placas de teste.
- Ao menos uma placa cadastrada como roubada na base de sinistros.
- Pipeline em execução.

**Procedimento:**
1. Inserir manualmente placas de teste na base de sinistros (ou garantir que existam placas previamente cadastradas).
2. Apresentar ao pipeline imagens com as placas de teste (roubada e não roubada).
3. Verificar no banco se o campo `match` foi preenchido corretamente para cada scan.
4. Repetir o teste com 5 placas marcadas como roubadas e 5 placas não cadastradas.

**Critério de aceite:** 100% dos casos com placa roubada resultam em `match = true`; 100% dos casos com placa não cadastrada resultam em `match = false`.

---

#### TM-04 — Latência Total do Pipeline End-to-End

**Requisito coberto:** RNF-01

**Objetivo:** Medir o tempo total entre a captura de um frame com placa visível e a criação do scan correspondente no banco de dados, verificando se o limite de 5 segundos é respeitado.

**Pré-condições:**
- Pipeline completo em execução: drone → YOLO → OCR → matcher → `POST /api/scans/`.
- Instrumentação de tempo no `drone.py` ou `plate_recognizer.py` para registrar `t0` (captura do frame) e `t1` (resposta do POST ao backend).

**Procedimento:**
1. Instrumentar o pipeline com `time.time()` nos pontos de captura do frame e de confirmação do scan no banco.
2. Executar 10 leituras de placa com o drone em operação normal.
3. Calcular o delta `t1 - t0` para cada leitura.
4. Registrar média, mediana e valor máximo.

**Critério de aceite:** Mediana ≤ 5 s; nenhum caso individual ultrapassando 8 s.

---

#### TM-05 — Latência de Disparo de Alerta Crítico

**Requisito coberto:** RNF-02

**Objetivo:** Medir o tempo entre a identificação de um match positivo no backend e a disponibilização do alerta no endpoint `GET /api/scans/matches`, verificando se o limite de 2 segundos é respeitado.

**Pré-condições:**
- Backend em execução.
- Um scan com `match = true` é criado via `POST /api/scans/`.
- Frontend ou script monitorando `GET /api/scans/matches` em polling.

**Procedimento:**
1. Registrar o timestamp `t0` imediatamente antes do `POST /api/scans/` com `match = true`.
2. Realizar polling em `GET /api/scans/matches` a cada 200 ms até o novo scan aparecer.
3. Registrar `t1` no momento em que o scan for encontrado na resposta.
4. Calcular `t1 - t0`.
5. Repetir 5 vezes.

**Critério de aceite:** `t1 - t0` < 2 s em todos os casos.

---

#### TM-06 — Latência do Streaming de Vídeo no Dashboard

**Requisito coberto:** RNF-03

**Objetivo:** Medir o atraso entre um evento visual capturado pela câmera do drone e a exibição correspondente no dashboard do gestor, verificando se o limite de 5 segundos é respeitado.

**Pré-condições:**
- Drone DJI Tello em operação com streaming ativo (`streamon`).
- Dashboard em execução consumindo o feed de vídeo.
- Câmera de referência ou cronômetro visível simultaneamente ao drone e ao dashboard para medir o offset.

**Procedimento:**
1. Posicionar um cronômetro digital visível na cena capturada pelo drone.
2. Gravar a tela do dashboard durante 60 segundos de streaming.
3. Extrair frames do vídeo gravado e comparar o horário exibido no cronômetro da cena com o horário real dos frames.
4. Calcular a diferença média.

**Critério de aceite:** Latência média < 5 s.

---

#### TM-07 — Autenticação e Controle de Acesso da API

**Objetivo:** Verificar se as rotas protegidas do backend rejeitam requisições sem token válido e se o controle de papéis (`gestor_remoto`, `gestor_local`) está funcionando corretamente.

**Pré-condições:**
- Backend em execução.
- Usuários cadastrados com papéis distintos.

**Procedimento:**
1. Enviar requisições a rotas protegidas sem o header `Authorization` — verificar resposta `401`.
2. Enviar requisições com token expirado ou inválido — verificar resposta `401`.
3. Autenticar com usuário de papel `gestor_local` e tentar acessar rota exclusiva de `gestor_remoto` (ex.: `DELETE /api/scans/{sid}`) — verificar resposta `403`.
4. Autenticar com papel correto e verificar acesso permitido com resposta `200` ou `201`.

**Critério de aceite:** 100% dos casos acima retornam o código HTTP esperado.

---

## 4. Procedimentos Automatizados e Resultados

&emsp;Esta seção apresenta a **execução automatizada** de todos os testes do plano. Os procedimentos manuais da Seção 3 foram mantidos como referência — eles continuam válidos para sessões com o parceiro e com o drone físico —, e cada um recebeu aqui um equivalente automatizado: o julgamento humano foi substituído por critérios objetivos mensuráveis, e os recursos físicos indisponíveis no momento da execução (drone DJI Tello, avaliadores externos) foram substituídos por simulações controladas que preservam o caminho de código real do sistema. As limitações de generalização decorrentes dessas substituições são discutidas na Seção 5.

### 4.1 Infraestrutura de Automação e Tecnologias

&emsp;A automação foi implementada em dois scripts Python na raiz do repositório, executados contra o backend Flask local conectado ao banco PostgreSQL (Supabase) do projeto:

- **`run_tests_tm.py`** — executa TM-02, TM-03, TM-05 e TM-07 (testes de API e banco de dados).
- **`run_tests_auto.py`** — gera o dataset sintético de placas e executa TV-01, TV-02, TV-03, TM-01, TM-04 e TM-06. Os resultados ficam consolidados em `resultados_testes_auto.json`.

&emsp;Tecnologias utilizadas e o papel de cada uma:

| Tecnologia | Papel nos testes |
|------------|------------------|
| Python 3.12 | Runner de todos os testes |
| `requests` | Chamadas HTTP à API Flask (mesmos endpoints consumidos pelo frontend) |
| `psycopg2` | Verificação direta dos registros no PostgreSQL/Supabase (timestamps, vínculos, matches) |
| `PyJWT` | Forja de tokens expirados e com assinatura inválida para os casos negativos do TM-07 |
| OpenCV (`cv2`) + NumPy | Renderização do dataset sintético, métricas de qualidade de imagem (TV-01), codificação/decodificação de timestamp em frames de vídeo (TM-06) |
| Ultralytics YOLO26 (`license_plate_best.pt`) | Etapa de detecção de placas do pipeline real (TM-01, TM-04) |
| EasyOCR | Etapa de leitura de caracteres do pipeline real (TM-01, TM-04) |
| `sqlite3` | Fila local `plate_frames` (mesmo mecanismo do `local_detections.py`) para TM-03 e TM-04 |
| `http.server` (ThreadingHTTPServer) | Servidor MJPEG local simulando o feed de vídeo do drone (TM-06) |
| `threading` | Telemetria simulada do drone (TV-03) e servidor de streaming em paralelo (TM-06) |
| `time.perf_counter` | Cronometragem de todas as medições de latência |

&emsp;**Dataset sintético de placas:** como não há dataset com ground truth no repositório nem acesso ao drone físico, foi gerado um conjunto reprodutível (semente fixa 42) de 50 imagens sintéticas (`dataset_placas/` + `ground_truth.json`), com placas brasileiras nos formatos antigo (LLLNNNN) e Mercosul (LLLNLNN) renderizadas com OpenCV e compostas em cenas que variam **distância** (placa com 420 px, 260 px ou 150 px de largura), **iluminação** (normal; escura com ganho 0,55; clara com ganho 1,35), **ângulo** (0°, ±5°, ±8°), além de ruído de sensor e desfoque gaussiano nas imagens distantes.

&emsp;**Higiene de dados:** todos os registros criados pelos testes (scans, veículos, usuários e drones de teste) são removidos do banco ao final de cada execução, e as pastas de frames de evidência geradas em `src/uploaded_frames/` durante os testes foram apagadas.

---

### 4.2 TV-01 — Qualidade das Imagens (automatizado)

**Adaptação:** os dois avaliadores humanos foram substituídos por um classificador objetivo de qualidade. A classificação em _"adequada"_, _"aceitável com ressalvas"_ ou _"inadequada"_ é derivada de quatro métricas calculadas com OpenCV **sobre a região da placa** (que é o que confere valor de evidência à imagem): nitidez (variância do Laplaciano), brilho médio, contraste (desvio padrão) e resolução mínima da cena. Limiares: _adequada_ exige nitidez ≥ 100, brilho entre 60 e 200, contraste ≥ 40 e resolução ≥ 640×480; _aceitável_ exige nitidez ≥ 50, brilho entre 40 e 220 e contraste ≥ 25; abaixo disso, _inadequada_ (o limiar de nitidez segue a heurística usual de detecção de desfoque por variância do Laplaciano).

**Procedimento executado:** para cada uma das 50 imagens do dataset, recortar a região da placa pelo ground truth, calcular as métricas, classificar pela pior métrica e somar o percentual aproveitável.

**Resultados (12/06/2026):**

| Métrica | Valor |
|---------|-------|
| Imagens avaliadas | 50 |
| Adequadas | 30 (60%) |
| Aceitáveis com ressalvas | 20 (40%) |
| Inadequadas | 0 |
| **Percentual aproveitável** | **100%** |

&emsp;**Resultado: ✅ Aprovado** (critério: ≥ 80%). As imagens em iluminação escura caíram para _aceitável_ (brilho do recorte entre 49 e 77), mas nenhuma ficou ilegível; as imagens em iluminação normal/clara apresentaram nitidez entre 920 e 5.390, muito acima do limiar.

---

### 4.3 TV-02 — Fluxo da Central de Alertas (automatizado)

**Adaptação:** o avaliador humano foi substituído por um cliente automatizado que executa as mesmas tarefas do roteiro original, na mesma ordem, usando os mesmos endpoints que o frontend consome (`/api/auth/login`, `/api/scans/pendentes`, `/api/scans/:id`, `/api/drones/:id`, `/api/operacoes/:id`, `PATCH /api/scans/:id/validar`), com cronometragem individual por tarefa. O questionário de satisfação (subjetivo) foi substituído por uma verificação objetiva de completude: a tarefa "visualizar informações" só é bem-sucedida se placa, zona, data/hora e imagem estiverem presentes nas respostas da API.

**Procedimento executado:** criar dois scans de teste `match = true` pendentes com imagem; autenticar como operador `gestor_local`; acessar a fila de pendentes; localizar os dois alertas; visualizar as informações de um deles; aprovar o primeiro e rejeitar o segundo; somar os tempos.

**Resultados (12/06/2026):**

| Tarefa | Duração | Sucesso |
|--------|---------|---------|
| T1 — Login do operador | 0,288 s | ✅ |
| T2 — Acessar Central de Alertas | 0,060 s | ✅ |
| T3 — Localizar alertas pendentes | < 0,001 s | ✅ (2/2) |
| T4 — Visualizar informações do alerta | 0,179 s | ✅ (placa, zona, data/hora e imagem presentes) |
| T5 — Aprovar alerta 1 | 0,185 s | ✅ HTTP 200 |
| T6 — Rejeitar alerta 2 | 0,164 s | ✅ HTTP 200 |
| **Total** | **0,876 s** | **✅** |

&emsp;**Resultado: ✅ Aprovado** (critério: fluxo completo ≤ 180 s com informações completas). O teste valida a viabilidade funcional e a completude de dados do fluxo; a avaliação de usabilidade subjetiva (intuitividade, clareza visual) continua exigindo a sessão com usuário da Seção 3.

---

### 4.4 TV-03 — Conectividade dos Drones (automatizado)

**Adaptação:** o avaliador diante da tela OperationsManager foi substituído por um monitor programático que consome os mesmos dados da tela (`GET /api/drones/:id` — `status_voo`, `bateria`, `conectividade`). A telemetria do drone é simulada por uma thread que envia `PATCH /api/drones/:id/localizacao` a cada 1 s, como um cliente real. Dois cenários: **(A)** telemetria interrompida abruptamente, sem aviso (queda real de conexão); **(B)** o cliente do drone reporta `status_voo = "offline"` antes de cair.

**Procedimento executado:** criar drone de teste em operação ativa; confirmar estado conectado com telemetria ativa por 5 s; cenário A — interromper a telemetria e monitorar a API por 60 s buscando qualquer sinal de desconexão; cenário B — enviar o PATCH de offline e medir o tempo até o estado refletir na API.

**Resultados (12/06/2026):**

| Cenário | Detectado? | Tempo |
|---------|-----------|-------|
| A — Telemetria interrompida abruptamente | ❌ Não (60 s de observação) | — |
| B — Drone reporta `offline` antes de cair | ✅ Sim | imediato (primeira consulta) |

&emsp;**Resultado: ❌ Reprovado no critério principal** (critério: desconexão identificável em ≤ 30 s). Quando a telemetria simplesmente para — o cenário realista de perda de conexão — **nenhum dado exposto pela API permite distinguir o drone desconectado**: o backend não registra o horário da última telemetria (não há `last_seen`) nem possui rotina que marque drones silenciosos como `offline`. A interface continua exibindo o último estado conhecido (`em_voo`, bateria 90%) indefinidamente. A detecção só funciona se o próprio drone avisar que vai cair (cenário B), o que contraria o espírito do RNF-05. Correção proposta na Seção 5.

---

### 4.5 TM-01 — Acurácia do Pipeline (automatizado)

**Adaptação:** na ausência de dataset real com ground truth e do drone para a etapa de capturas em tempo real, o teste foi executado sobre o dataset sintético de 50 imagens (Seção 4.1). Além da acurácia do pipeline completo (`process_frame`: YOLO26 + EasyOCR), mediu-se a acurácia do **estágio de OCR isolado** (`recognize_plate` sobre o recorte exato da placa), para separar falhas de detecção de falhas de leitura. O estado de estabilização entre frames (`plate_history`) é zerado entre imagens.

**Procedimento executado:** para cada imagem, rodar `process_frame` e registrar a placa de maior confiança; rodar `recognize_plate` no recorte ground-truth; contabilizar correspondência exata; calcular taxa de detecção do YOLO, acurácia do pipeline e do OCR isolado.

**Resultados (12/06/2026):**

| Métrica | Resultado |
|---------|-----------|
| Taxa de detecção do YOLO26 | 66% (33/50) |
| Acurácia do pipeline completo (YOLO + OCR) | **50% (25/50)** |
| Acurácia do OCR isolado (recorte correto) | 74% (37/50) |

&emsp;**Resultado: ❌ Reprovado no cenário sintético** (critério: ≥ 80%). Dois gargalos distintos: **(1) detecção** — o YOLO26, treinado com fotografias reais, não generaliza para imagens renderizadas, falhando principalmente nas placas distantes (150 px); **(2) leitura** — mesmo com recorte perfeito, o OCR erra 26% dos casos, com confusões entre caracteres semelhantes (ex.: `A`→`N` em baixa nitidez; `H`→`4` no caso `FLG8H68` lido como `FLG8468`) e degradação nas imagens escuras. Este resultado não substitui a medição com imagens reais exigida pelo RNF-04 — placas reais (tipografia FE-Schrift, refletividade, contexto) podem melhorar a detecção e piorar o ruído; ver Seção 5.

---

### 4.6 TM-02 — Registro Temporal e de Zona (automatizado)

**Adaptação:** o envio pelo pipeline foi substituído por 5 `POST /api/scans/` diretos (mesma rota usada pelo pipeline), guardando o horário UTC imediatamente anterior a cada POST; a verificação combinou `GET /api/scans/:id` e consulta SQL com JOIN `scans → drones → operacoes`.

**Resultados (12/06/2026):** 5/5 scans com `horario_scan` preenchido; 5/5 vinculados à operação ativa com zona ("Base Principal"); coerência temporal entre 0,27 s e 0,76 s. **Resultado: ✅ Aprovado (100%).**

---

### 4.7 TM-03 — Base de Sinistros (automatizado)

**Adaptação:** as imagens apresentadas ao pipeline foram substituídas por detecções inseridas diretamente na fila SQLite `plate_frames` (mesma estrutura do `local_detections.py`), processadas pelo código real `supabase_matcher.process_pending_detections()`. Foram inseridas 5 placas de teste na base de sinistros (`veiculos`, `roubado = true`) e usadas 5 placas não cadastradas.

**Resultados (12/06/2026):** 5/5 placas roubadas → `match = true` com `imagem_url` preenchida; 5/5 não cadastradas → `match = false`. **Resultado: ✅ Aprovado (10/10, 100%).**

---

### 4.8 TM-04 — Latência End-to-End (automatizado)

**Adaptação:** a captura pelo drone foi substituída por leitura de imagem estática (`cv2.imread`) — modo já previsto no procedimento original. Cadeia real medida: leitura do frame → YOLO26 + EasyOCR (`process_frame`) → inserção na fila SQLite → `supabase_matcher.process_pending_detections()` → scan visível no banco PostgreSQL. Nos frames em que o CV não produziu leitura válida (limitação do TM-01), a placa ground-truth foi usada como fallback para medir o restante da cadeia — o tempo de CV consumido permanece contabilizado. 5 das 10 placas foram pré-cadastradas como roubadas, exercitando o caminho com match e gravação de frame de evidência.

**Resultados (12/06/2026):**

| Métrica | Valor |
|---------|-------|
| Leituras | 10 (10/10 scans criados no banco) |
| Mediana | **0,914 s** |
| Média | 1,004 s |
| Mínimo / Máximo | 0,252 s / 2,197 s |
| Tempo da etapa de CV (YOLO+OCR, CPU) | 0,06 s a 1,96 s por frame |

&emsp;**Resultado: ✅ Aprovado** (critério: mediana ≤ 5 s, nenhum caso > 8 s). A etapa de visão computacional domina o tempo; matching e persistência no banco remoto somam ~0,2–0,3 s. O enlace Wi-Fi do Tello não está representado.

---

### 4.9 TM-05 — Latência de Alerta Crítico (automatizado)

**Adaptação de procedimento (achado):** o procedimento original previa polling em `GET /api/scans/matches`, mas esse endpoint **filtra `status_validacao = 'aprovado'`** — um scan recém-criado (pendente) nunca aparece nele antes da validação humana, e o procedimento original falha por construção (confirmado em execução: timeout de 15 s sem o alerta aparecer). A medição foi dividida em duas etapas: **(1)** criação do match → alerta disponível na API (`GET /api/scans/?match=true`); **(2)** aprovação → publicação em `GET /api/scans/matches` (endpoint consumido pela Central de Alertas).

**Resultados (12/06/2026), 5 repetições:**

| Etapa | Média | Máximo |
|-------|-------|--------|
| Match criado → alerta disponível na API | 0,219 s | 0,227 s |
| Aprovação → publicado em `/scans/matches` | 0,167 s | 0,182 s |

&emsp;**Resultado: ✅ Aprovado nas duas etapas** (critério: < 2 s em todos os casos). O achado de contrato entre frontend e API está registrado na Seção 5.

---

### 4.10 TM-06 — Latência de Streaming (automatizado)

**Adaptação:** sem o drone físico, o feed UDP do Tello foi substituído por um **servidor MJPEG local a 30 fps** cujos frames carregam o timestamp de geração codificado em 48 blocos binários (robustos à compressão JPEG), além de um relógio legível — um "cronômetro embutido" verificável por software, no lugar do cronômetro físico do procedimento original. O consumidor replica o mecanismo real do sistema (`cv2.VideoCapture` com descarte de buffer, exatamente como em `src/visao_computacional/drone.py`); a latência de cada amostra é a diferença entre o horário de leitura e o timestamp embutido no frame.

**Resultados (12/06/2026):**

| Métrica | Valor |
|---------|-------|
| Amostras válidas (12 s de streaming) | 113 |
| Latência média | **0,039 s** |
| Mínima / Máxima | 0,037 s / 0,044 s |

&emsp;**Resultado: ✅ Aprovado** (critério: média < 5 s). O mecanismo de consumo com buffer mínimo mantém a latência na casa de dezenas de milissegundos em rede local; o enlace Wi-Fi/UDP do drone real não está representado.

---

### 4.11 TM-07 — Autenticação e Controle de Acesso (automatizado)

**Adaptação:** os tokens adversariais foram forjados com PyJWT — um **expirado** (assinado com o segredo real e `exp` no passado) e um **com assinatura inválida** (assinado com segredo errado) — além do caso sem header e dos casos de papel via usuário `gestor_local` criado pelo próprio teste.

**Resultados (12/06/2026):**

| Caso | Esperado | Obtido | |
|------|----------|--------|---|
| Sem token | 401 | 401 | ✅ |
| Token expirado | 401 | 401 | ✅ |
| Token com assinatura inválida | 401 | **422** | ❌ |
| `gestor_local` em rota de `gestor_remoto` (DELETE) | 403 | 403 | ✅ |
| Papel correto — GET | 200 | 200 | ✅ |
| Papel correto — POST | 201 | 201 | ✅ |

&emsp;**Resultado: Reprovado parcialmente (5/6).** Tokens com assinatura inválida retornam `422` em vez de `401` — comportamento padrão do flask-jwt-extended sem um `invalid_token_loader` customizado no `create_app`. O acesso permanece bloqueado (sem falha de segurança), mas o código contraria o critério e pode confundir clientes que tratam `401` como gatilho de renovação de sessão.

---

## 5. Análise Crítica dos Resultados Automatizados

&emsp;Esta seção discorre sobre a adequação do sistema aos requisitos, os testes com resultado abaixo do esperado e suas causas prováveis, os limites de generalização dos resultados, os pontos de melhoria identificados e a relação com as hipóteses técnicas da Sprint 3.

### 5.1 Resumo Geral

| Teste | Requisitos | Resultado | Observação-chave |
|-------|-----------|-----------|------------------|
| TV-01 | RF-01 | Aprovado | 100% das imagens aproveitáveis como evidência (métricas objetivas) |
| TV-02 | RF-05 | Aprovado | Fluxo completo da Central de Alertas em 0,9 s via API, dados completos |
| TV-03 | RF-06, RNF-05 | Reprovado | Desconexão abrupta de drone é **indetectável** — falta heartbeat/last_seen |
| TM-01 | RF-02, RNF-04 | Reprovado | Pipeline 50%, OCR isolado 74% em dataset sintético (meta: 80%) |
| TM-02 | RF-03 | Aprovado | 100% dos scans com timestamp e vínculo de zona/operação |
| TM-03 | RF-04 | Aprovado | 10/10 matches corretos na base de sinistros |
| TM-04 | RNF-01 | Aprovado | Mediana 0,9 s (limite: 5 s), máx 2,2 s |
| TM-05 | RNF-02 | Aprovado | Alerta disponível em ~0,22 s (limite: 2 s) |
| TM-06 | RNF-03 | Aprovado | Latência média de 0,04 s no consumidor de vídeo |
| TM-07 | Segurança | Parcial (5/6) | Token inválido retorna 422 em vez de 401 |

&emsp;Em síntese: a **camada de backend e dados está sólida** — registro temporal/zona, matching de sinistros, latências de pipeline, de alerta e de streaming passaram com folga ampla em todos os critérios. As reprovações concentram-se em dois pontos estruturais: a **acurácia do reconhecimento** (TM-01) e a **observabilidade de conectividade dos drones** (TV-03), além de um ajuste pontual de contrato HTTP (TM-07).

### 5.2 Resultados Abaixo do Esperado e Causas Prováveis

&emsp;**TM-01 (acurácia 50% pipeline / 74% OCR).** A decomposição por estágio mostra que o problema não é único. A detecção (66%) falha sobretudo nas placas distantes — o YOLO26 foi fine-tuned com fotografias reais e não generaliza para o render sintético, o que era esperado e está sinalizado como limitação do método. Já o OCR, mesmo recebendo o recorte perfeito da placa, erra 26% — confusões entre caracteres visualmente próximos (`A`/`N`, `H`/`4`, `0`/`O`) e degradação acentuada em baixa iluminação. Como as regras de correção do `plate_recognizer.py` forçam o caractere ao tipo esperado pela posição (letra/dígito), erros que respeitam o formato passam silenciosamente — ou seja, a placa retornada é *válida* mas *errada*, o que em produção geraria consulta de sinistro contra placa inexistente.

&emsp;**TV-03 (desconexão indetectável).** O esquema atual do banco não armazena o horário da última telemetria (`last_seen`) e não existe rotina (job ou verificação on-read) que reclassifique drones silenciosos como `offline`. O fluxo de dados é apenas *push*: o drone atualiza seu estado via PATCH. Consequência direta: a queda real de conexão — justamente o evento que o RF-06 quer detectar — não produz nenhum sinal observável na interface, que segue exibindo o último estado conhecido indefinidamente.

&emsp;**TM-07 (422 vs 401).** Ausência de handlers customizados (`invalid_token_loader`) na inicialização do JWT em `app/__init__.py`; o flask-jwt-extended responde `422` por padrão para tokens estruturalmente inválidos. Sem impacto de segurança (acesso negado em todos os casos), mas fora do contrato esperado.

&emsp;**Achado adicional (TM-05/RF-05):** `GET /api/scans/matches` retorna apenas scans **aprovados**. Como a Central de Alertas consome esse endpoint, um match recém-detectado (pendente) não aparece para o operador por esse caminho — o "alerta imediato" do RF-05 depende de o operador olhar a fila de pendentes. A latência técnica do backend é excelente (~0,2 s); o gargalo é semântico, no contrato entre frontend e API.

### 5.3 Limites de Generalização

1. **Dataset sintético (TV-01, TM-01, TM-04):** placas renderizadas não reproduzem tipografia FE-Schrift real, refletividade, sujeira, desfoque de movimento nem artefatos do encoder do Tello. Os números de acurácia valem como diagnóstico de robustez relativa (quais condições degradam o quê), não como medida final do RNF-04 — que exige repetição com imagens reais.
2. **Ausência do drone físico (TM-04, TM-06):** as latências medidas excluem o enlace Wi-Fi/UDP do Tello. TM-06, em particular, valida o *consumidor* de vídeo (que mantém ~40 ms), não o transporte.
3. **Avaliação de usabilidade por proxy (TV-01, TV-02):** métricas objetivas e completude de dados substituem bem o critério quantitativo, mas não capturam intuitividade, hierarquia visual ou satisfação — a sessão com usuário real (procedimentos da Seção 3) continua valiosa antes da entrega ao parceiro.
4. **Ambiente de execução:** backend local + banco Supabase remoto (região sa-east-1), CPU sem aceleração. Latências de rede até o banco (~0,15–0,3 s por round-trip) estão embutidas nas medições — em produção com backend hospedado, tendem a cair.

### 5.4 Pontos de Melhoria Identificados

1. **Health check real de drones (corrige TV-03):** adicionar coluna `last_seen` atualizada a cada telemetria recebida e expor o estado derivado na API (ex.: `desconectado` quando `now - last_seen > 15 s`), via job periódico ou cálculo na leitura. O frontend passa a ter sinal confiável sem depender do drone "avisar que caiu".
2. **Handler de token inválido (corrige TM-07):** registrar `@jwt.invalid_token_loader` (e `unauthorized_loader`) no `create_app` devolvendo `401` uniformemente.
3. **Alertas pendentes na Central de Alertas (corrige o achado do TM-05):** o frontend deve consumir a fila de pendentes com match (ou o endpoint `/matches` deixar de filtrar por `aprovado`), garantindo que o alerta chegue ao operador no momento da detecção.
4. **Robustez do OCR (endereça TM-01):** ampliar o pré-processamento (equalização adaptativa/CLAHE para cenas escuras), considerar verificação cruzada com segunda leitura em frame subsequente antes de consultar a base, e montar um dataset real anotado (mesmo pequeno) para medir o RNF-04 em condições de operação.
5. **Fine-tuning com dados aumentados:** incluir amostras sintéticas e capturas do Tello no treino do detector para reduzir a sensibilidade a domínio observada no TM-01.

### 5.5 Relação com as Hipóteses da Sprint 3

&emsp;As hipóteses levantadas na Sprint 3 sobre as limitações do OCR foram **corroboradas** pelos dados do TM-01: (i) a leitura degrada com distância e baixa iluminação — as falhas concentraram-se exatamente nessas condições; (ii) os caracteres ambíguos são a principal fonte de erro de leitura — observado diretamente nos casos `A`→`N` e `H`→`4`; e (iii) a correção posicional por formato (letra/dígito) mascara erros em vez de eliminá-los, pois produz placas sintaticamente válidas porém incorretas. O dado novo desta sprint é a quantificação da contribuição de cada estágio (detecção vs. leitura) e a constatação de que o restante da cadeia — matching, persistência e alerta — opera com folga de latência superior a 80% em relação aos limites dos RNFs, ou seja, há orçamento de tempo disponível para estratégias de leitura mais caras (múltiplos frames, segunda passada de OCR) sem violar o RNF-01.


## 6. Testes de Usuário

&emsp;Os testes com usuários reais estão planejados para a Sprint 5 e serão conduzidos em duas fases. Na **primeira fase**, a própria equipe de desenvolvimento executa os roteiros internamente para identificar falhas grosseiras antes de expor o produto a participantes externos. Na **segunda fase**, alunos do campus do Inteli são convidados a usar o sistema enquanto um integrante da equipe observa e registra as respostas em uma tabela de resultados mantida na documentação da Sprint 5. Cada sessão tem duração máxima de **20 minutos** e foca exclusivamente no uso do produto.

### 6.1 Escopo dos Testes

&emsp;Os três roteiros da Seção 3.1 orientam a sessão, adaptados para o tempo disponível:

| Roteiro | Foco | Critério de aceite |
|---------|------|-------------------|
| TV-01 | O participante consegue identificar o veículo e a placa nas imagens de evidência? | ≥ 80% das imagens classificadas como adequadas ou aceitáveis |
| TV-02 | O participante consegue localizar um alerta pendente, visualizar as informações e aprovar ou rejeitar — sem orientação? | Fluxo completo em até 3 minutos sem assistência |
| TV-03 | O participante consegue identificar, apenas pela interface, qual drone está desconectado? | Identificação correta em até 30 segundos |

### 6.2 Registro de Resultados

&emsp;Os resultados de cada sessão são registrados por um integrante da equipe diretamente na tabela de acompanhamento da Sprint 5. A tabela identifica os participantes de forma anônima (P1, P2 …) e registra, por roteiro: se a tarefa foi concluída, o tempo gasto e observações coletadas durante a sessão.

&emsp;A tabela de registro está disponível em [Sprint 5 — Testes de Usuário](../../sprint-5/Testes/resultados-testes-usuario).

