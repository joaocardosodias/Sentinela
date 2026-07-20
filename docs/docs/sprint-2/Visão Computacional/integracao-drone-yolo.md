---
sidebar_position: 3
---

# Integração do Drone com Visão Computacional


&emsp; O foco desta sprint foi o desenvolvimento do modelo de visão computacional para reconhecimento de placas veiculares e sua integração com o drone DJI Tello. Com o drone já conectado ao computador (documentado em [Código do Drone](./conexao_drone.md)), o **modelo YOLO**, responsável pela detecção das placas, juntamente com o **OCR** utilizado para reconhecimento dos caracteres, passou a rodar diretamente sobre o stream de vídeo da câmera do drone.

&emsp; Ao final da sprint, o sistema é capaz de reconhecer placas nos padrões brasileiro antigo (LLLNNNN) e Mercosul (LLLNLNN) a partir do vídeo do drone em tempo real. O principal limitador identificado foi o **delay no stream de vídeo**, que será endereçado na próxima sprint.

---

## Organização do Código

&emsp; O código foi estruturado em dois arquivos independentes, permitindo que cada parte seja alterada sem impactar a outra:

- **`plate_recognizer.py`** — contém o modelo YOLO, o OCR e toda a lógica de reconhecimento e validação de placas.
- **`drone.py`** — responsável pela comunicação com o drone e pela exibição do vídeo. Importa o reconhecimento do arquivo acima.

---

## Como a Integração Funciona

&emsp; O pipeline completo de processamento ocorre da seguinte forma:

1. O DJI Tello transmite vídeo via stream UDP
2. O `drone.py` captura os frames utilizando OpenCV
3. Os frames são enviados para `process_frame`
4. O YOLO detecta possíveis placas no frame
5. O OCR realiza a leitura dos caracteres detectados
6. O padrão da placa é validado
7. O frame anotado é exibido em tempo real

&emsp; A integração entre os dois arquivos é realizada por meio de um `import` direto. O `drone.py` importa a função `process_frame` do `plate_recognizer.py`:

```python
from plate_recognizer import process_frame
```

&emsp; A função `process_frame` recebe um frame de vídeo (array BGR), executa o YOLO e o OCR, desenha as anotações diretamente na imagem e retorna o frame anotado junto com a lista de resultados detectados. No loop de vídeo do `drone.py`, o uso fica:

```python
frame, frame_results = process_frame(frame)

if frame_results:
    print(frame_results)

cv2.imshow("Video do Tello", frame)
```

&emsp; Com isso, o vídeo da câmera do drone exibe as bounding boxes e o texto da placa reconhecida sobrepostos ao frame em tempo real.

---

## Delay no Stream de Vídeo

&emsp; Após a integração, foi identificado um delay significativo no vídeo, com travamentos frequentes. O reconhecimento em si funcionava (as detecções eram registradas no terminal), porém a janela de vídeo atrasava a ponto de o resultado não aparecer na tela em vários momentos.

&emsp; Uma hipótese é que parte do problema seja de rede, dado que o stream do drone trafega via UDP sobre Wi-Fi, protocolo que não garante entrega nem ordenação dos pacotes. Além disso, o custo computacional do YOLO e do OCR por frame contribui para o acúmulo de atraso.

&emsp; Foram implementadas três otimizações para reduzir a latência gerado pelo lado do processamento:

### 1. Buffer mínimo do OpenCV

&emsp; Por padrão, o OpenCV mantém um buffer interno com vários frames. Quando o YOLO demora para processar, esses frames se acumulam e o vídeo exibe informações defasadas. O buffer foi configurado para o valor mínimo:

```python
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
```

### 2. Descarte de frames acumulados (flush)

&emsp; Mesmo com buffer reduzido, pacotes UDP podem se acumular antes da leitura. Para garantir que sempre seja lido o frame mais recente, frames são descartados com `grab()` antes de cada `read()`. O método `grab()` captura o frame sem decodificá-lo, sendo significativamente mais barato que `read()`:

```python
def flush_buffer(cap, n=5):
    for _ in range(n):
        cap.grab()
```

### 3. Inferência YOLO a cada N frames

&emsp; A inferência do YOLO e o OCR são as operações mais custosas do pipeline. Em vez de executá-las em todos os frames, a detecção ocorre a cada 3 frames. Nos frames intermediários, o vídeo é exibido sem processamento de inferência, mantendo a fluidez visual sem comprometer a detecção:

```python
YOLO_EVERY_N_FRAMES = 3

if frame_count % YOLO_EVERY_N_FRAMES == 0:
    last_annotated_frame, frame_results = process_frame(frame)
else:
    last_annotated_frame = frame  # exibe frame cru entre as detecções
```

&emsp; As otimizações reduziram o delay, mas não o eliminaram. A investigação e melhoria de performance são o foco da próxima sprint.

---

## Resultado Atual

&emsp; O sistema atual reconhece placas a partir do vídeo do drone. Quando o pipeline processa o frame a tempo, a placa e seu formato (BR_OLD ou BR_MERCOSUL) são exibidos sobre o vídeo. Mesmo nos casos em que o delay impede a exibição na janela, a detecção é registrada no terminal.

&emsp; Abaixo, o terminal registrando a detecção de uma placa em tempo real:

<div align="center">    
    <sup>Figura 1: Terminal com reconhecimento da placa</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1778804420/Design_sem_nome_tczu2w.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>

&emsp; Quando o frame é processado a tempo, o resultado aparece anotado diretamente na janela de vídeo:

<div align="center">    
    <sup>Figura 2: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1778804721/2e577bbe-3af7-4278-a43e-5d99b89ed22f.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>


&emsp; A seguir, uma demonstração do reconhecimento acontecendo em tempo real:

<div align="center">
    <p>Figura 3: GIF da detecção da placa</p>

    <img 
        src="/img/sprint-2/reconhecimento-placa.gif" 
        alt="GIF demonstrando a detecção de placas em tempo real"
        width="900"/>
    <p>Fonte: Autoria própria (2026).</p>
</div>

---

## Próximos Passos

&emsp; Para a próxima sprint, o foco será a melhoria de performance do stream e da qualidade do reconhecimento:

- Investigar se o gargalo de delay é predominantemente de rede ou de processamento
- Avaliar tratamentos de imagem para melhorar a qualidade dos frames recebidos
- Avaliar se a redução da resolução do stream reduz o delay sem prejudicar o reconhecimento