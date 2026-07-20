---
sidebar_position: 3
title: Otimização do Delay da Câmera
---

# Otimização do Delay da Câmera do Drone

Na integração inicial entre o drone DJI Tello e o reconhecimento de placas, o sistema já conseguia capturar o stream de vídeo, detectar placas com YOLO e ler os caracteres com OCR. Porém, a janela da câmera apresentava atraso perceptível. Esse atraso não vinha apenas da rede Wi-Fi do drone; ele também era causado pela forma como o processamento pesado era executado junto com a exibição do vídeo.

A branch `fix/drone-camera-delay` reduziu esse delay ao mudar a arquitetura do loop de vídeo. A câmera passou a priorizar a exibição do frame mais recente, enquanto o reconhecimento de placas roda em paralelo e sem acumular fila de frames antigos.

## Problema Observado

Antes da alteração, o mesmo loop fazia três tarefas ao mesmo tempo:

1. Ler o frame da câmera.
2. Executar YOLO e OCR no frame.
3. Exibir o frame anotado na janela.

O ponto crítico estava na chamada síncrona para `process_frame(frame)`. Essa função executa a inferência do YOLO, recorta a placa, aplica OCR e valida o texto reconhecido. Enquanto esse processamento acontecia, o loop da câmera ficava bloqueado e deixava de atualizar a janela.

```python
if frame_count % YOLO_EVERY_N_FRAMES == 0:
    last_annotated_frame, frame_results = process_frame(frame)
else:
    last_annotated_frame = frame

cv2.imshow("Video do Tello", last_annotated_frame)
```

Mesmo processando apenas um frame a cada três, quando o YOLO e o OCR demoravam, o vídeo ficava parado esperando a inferência terminar. Nesse intervalo, novos frames continuavam chegando pelo stream UDP e podiam se acumular no buffer. O resultado era uma câmera visualmente atrasada: a janela não mostrava necessariamente o estado mais recente visto pelo drone.

## Alterações Implementadas

| Alteração | Como foi feita | Por que ajuda |
| --- | --- | --- |
| Processamento assíncrono | Uso de `ThreadPoolExecutor(max_workers=1)` para rodar YOLO + OCR fora do loop principal da câmera. | A exibição do vídeo não precisa esperar a inferência terminar. |
| Sem fila acumulada de inferências | Um novo processamento só é iniciado quando `processing_future is None`. | Evita processar frames antigos depois que eles já perderam valor para o vídeo ao vivo. |
| Desenho do último resultado no frame atual | `draw_detection_results` aplica as últimas detecções conhecidas sobre o frame mais recente. | A janela continua ao vivo, sem voltar a exibir o frame antigo que foi processado. |
| Controle de frequência | `YOLO_EVERY_N_FRAMES = 3` e `MIN_SECONDS_BETWEEN_DETECTIONS = 0.25`. | Reduz a chance de saturar CPU/GPU com chamadas consecutivas de YOLO + OCR. |
| Redução de buffer | `cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)` e descarte de frames com `cap.grab()`. | Diminui a leitura de frames acumulados e prioriza o frame mais recente. |
| Backend de vídeo explícito | `cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)`. | Torna a captura UDP mais previsível no OpenCV. |
| Carregamento mais robusto do modelo | Caminho do peso definido por `Path(__file__).resolve().with_name("license_plate_best.pt")`. | Evita erro de caminho quando o script é executado a partir de outro diretório. |
| Uso seguro de aceleração | `easyocr.Reader(..., gpu=torch_accelerator_available())`. | Usa GPU quando disponível e evita forçar aceleração em ambientes sem suporte. |

## Novo Fluxo da Câmera

O novo loop separa a responsabilidade de exibir vídeo da responsabilidade de reconhecer placas:

```python
if should_process:
    processing_future = executor.submit(run_plate_recognition, frame.copy())
    next_processing_at = now + MIN_SECONDS_BETWEEN_DETECTIONS

display_frame = frame.copy()

if has_recent_results:
    draw_detection_results(display_frame, last_frame_results)

cv2.imshow(WINDOW_NAME, display_frame)
```

Com isso, o frame exibido é sempre baseado na leitura atual da câmera. O processamento recebe uma cópia do frame, roda em uma thread separada e devolve apenas os resultados estruturados, como bounding box, placa reconhecida, formato e confiança.

Quando o processamento termina, o resultado é armazenado em `last_frame_results`. Durante um curto período, definido por `DETECTION_OVERLAY_TTL_SECONDS = 1.5`, esses resultados são desenhados nos frames atuais.

## Por Que o Delay Diminuiu

### 1. A câmera parou de esperar o YOLO e o OCR

YOLO e OCR são as etapas mais custosas do pipeline. Na versão anterior, cada inferência atrasava a próxima atualização visual da câmera. Na versão nova, o vídeo continua sendo lido e exibido enquanto a inferência acontece em paralelo.

Essa mudança reduz o delay percebido porque a janela deixa de depender do tempo total de `process_frame(frame)`.

### 2. Frames antigos deixaram de formar fila

Uma solução assíncrona sem controle poderia criar outro problema: acumular vários frames aguardando processamento. Isso aumentaria o atraso, porque o sistema continuaria analisando imagens antigas mesmo depois de a cena já ter mudado.

A implementação evita esse comportamento ao permitir apenas uma inferência ativa por vez:

```python
should_process = (
    processing_future is None
    and frame_count % YOLO_EVERY_N_FRAMES == 0
    and now >= next_processing_at
)
```

Se o YOLO + OCR ainda estiver rodando, o sistema não agenda outro frame. Assim, a prioridade continua sendo manter o vídeo atual, não processar todo o histórico capturado.

### 3. O resultado é reutilizado sem reexibir o frame antigo

Na versão anterior, o frame anotado retornado por `process_frame` era o próprio frame processado. Se o processamento demorasse, esse frame já chegava atrasado para a janela.

Na versão nova, a função `run_plate_recognition` retorna os dados da detecção, e `draw_detection_results` desenha esses dados sobre o frame atual. Isso troca precisão temporal absoluta do overlay por fluidez do vídeo ao vivo. Para a experiência de operação, essa troca é melhor porque a câmera continua responsiva.

### 4. O buffer da câmera é mantido pequeno

O stream do Tello chega via UDP. Se o programa demora para consumir frames, o OpenCV pode continuar entregando imagens antigas acumuladas. Para reduzir esse efeito, o código configura buffer mínimo e descarta frames antes de ler:

```python
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def flush_buffer(cap, n=BUFFER_FLUSH_FRAMES):
    for _ in range(n):
        cap.grab()
```

O método `grab()` avança a captura sem decodificar completamente o frame, então ele é mais barato do que ler e processar cada imagem descartada. Isso ajuda o loop a se aproximar do frame mais recente disponível.

### 5. A frequência de inferência ficou limitada

Além de processar apenas a cada três frames, o código passou a respeitar um intervalo mínimo entre detecções:

```python
YOLO_EVERY_N_FRAMES = 3
MIN_SECONDS_BETWEEN_DETECTIONS = 0.25
```

Esse limite reduz competição por CPU/GPU entre captura, exibição, YOLO e OCR. Quando a máquina está sob carga, essa contenção é uma das causas de travamento visual.

## Resultado

A melhoria principal foi arquitetural: o vídeo deixou de ser bloqueado pela inferência. O reconhecimento de placas continua acontecendo, mas agora a janela da câmera prioriza frames recentes e só sobrepõe os resultados quando eles estão disponíveis.

Com isso, o delay diminuiu porque:

- o loop de câmera continua atualizando a janela enquanto YOLO + OCR rodam;
- frames antigos não entram em uma fila de processamento;
- o OpenCV é orientado a trabalhar com buffer mínimo;
- frames acumulados são descartados antes da leitura;
- a inferência é limitada por frame e por tempo.

## Limitações e Próximos Passos

A branch melhora a fluidez percebida, mas ainda não registra uma medição quantitativa de latência ou FPS antes e depois da alteração. Para validar numericamente a melhoria, os próximos testes devem registrar:

- FPS médio da janela de vídeo;
- tempo médio de `process_frame(frame)`;
- diferença entre timestamp de captura e timestamp de exibição;
- quantidade de inferências por segundo;
- comportamento em diferentes distâncias entre computador e drone.

Também é importante considerar que o overlay pode representar uma detecção feita até 1,5 segundo antes, por causa do tempo de vida definido em `DETECTION_OVERLAY_TTL_SECONDS`. Essa decisão foi tomada para favorecer a câmera ao vivo e evitar que a interface volte a exibir frames defasados.
