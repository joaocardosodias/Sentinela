---
sidebar_position: 1
title: Modelo de Classificação - YOLO11
---

# YOLO11: Teste do Modelo de Classificação V2

## Introdução

&emsp;Na Sprint 2, o pipeline de reconhecimento de placas veiculares foi construído utilizando o **YOLOv8n** como modelo de detecção. Aquela versão cumpriu seu papel como prova de conceito, validando o fluxo de captura, detecção, OCR e exibição dos resultados. Porém, como indicado na própria documentação da V1, a escolha do YOLOv8n foi uma decisão de engenharia voltada à prototipação, e a evolução natural do projeto seria comparar essa *baseline* com modelos mais recentes.

&emsp;Com esse objetivo, a Sprint 3 incluiu o teste do **YOLO11**, versão mais recente da família YOLO mantida pela Ultralytics. O YOLO11 traz melhorias arquiteturais significativas em relação ao YOLOv8. A proposta deste teste foi submeter o YOLO11n ao mesmo pipeline de *fine-tuning* e inferência usado anteriormente, avaliando se haveria ganhos mensuráveis de desempenho em relação ao YOLOv8n.

&emsp;Este documento descreve o processo de treinamento, os resultados obtidos, os problemas encontrados durante a execução local e a comparação direta com o modelo anterior.

---

## Ambiente de Treinamento

&emsp;O *fine-tuning* do YOLO11 foi realizado no **Google Colab**, utilizando os mesmos parâmetros de treinamento da V1 para garantir uma comparação justa entre os modelos.

| Parâmetro | Valor |
| --- | --- |
| **Plataforma** | Google Colab |
| **GPU** | Tesla T4 (15 GB VRAM) |
| **Modelo base** | `yolo11n.pt` (YOLO11 nano) |
| **Framework** | Ultralytics 8.4.56 |
| **Python** | 3.12.13 |
| **PyTorch** | 2.11.0+cu128 |
| **Dataset** | License-Plate-Recognition v13 (Roboflow) |
| **Imagens de treino** | 98.798 |
| **Imagens de validação** | 2.048 |
| **Épocas** | 5 |
| **Tamanho de imagem** | 640×640 |
| **Batch** | 16 |
| **Workers** | 2 |
| **Otimizador** | AdamW (lr=0.002, momentum=0.9) |

&emsp;O notebook do treinamento está disponível em [`YoloV11_CV.ipynb`](https://colab.research.google.com/drive/1VPsfnulhuLGSF7wmTR4U6nLj9nvZL34S?usp=sharing) e também versionado no repositório em `src/yolo11/YoloV11_CV.ipynb`.

---

## Arquitetura do YOLO11n

&emsp;O YOLO11n, apesar de ser a variante mais leve da família YOLO11, apresenta uma arquitetura mais sofisticada que o YOLOv8n. O sumário do modelo gerado pelo treinamento revela:

- **182 camadas** (vs. aproximadamente 168 no YOLOv8n)
- **2.590.035 parâmetros** (vs. ~3.2M no YOLOv8n)
- **6.4 GFLOPs** de custo computacional (vs. ~8.7 GFLOPs no YOLOv8n)

&emsp;Apesar de possuir mais camadas, o YOLO11n é **mais leve** que o YOLOv8n em termos de parâmetros e operações computacionais. Isso é possível graças aos novos blocos arquiteturais:

| Bloco | Função |
| --- | --- |
| **C3k2** | Bloco de convolução mais eficiente que o C2f do YOLOv8, usando kernels menores |
| **C2PSA** | Bloco de atenção espacial parcial cruzada, melhora o foco em regiões relevantes da imagem |
| **SPPF** | Spatial Pyramid Pooling Fast, para captura de contexto multiescala |

&emsp;O peso final gerado pelo treinamento (`license_plate_best.pt`) possui **5.5 MB**, tamanho compatível com deploy em dispositivos embarcados.

---

## Tempo de Processamento

&emsp;O treinamento completo de 5 épocas levou **aproximadamente 2 horas e 40 minutos** no Google Colab com GPU Tesla T4. O log do treinamento registrou um tempo total de **2.997 horas** (~3h), contabilizando treinamento e validação de todas as épocas.

| Época | Tempo de treino | Tempo de validação |
| --- | --- | --- |
| 1/5 | ~37 min | ~50 seg |
| 2/5 | ~35 min | ~16 seg |
| 3/5 | ~35 min | ~16 seg |
| 4/5 | ~35 min | ~15 seg |
| 5/5 | ~35 min | ~16 seg |

&emsp;A primeira época demora mais porque o modelo ainda está fazendo *warmup* dos parâmetros e cache do dataset. A partir da segunda época, o tempo estabiliza em torno de 35 minutos por época.

:::note
O tempo de ~2h40 é significativo para um modelo nano com apenas 5 épocas, mas isso se deve ao tamanho do dataset (98.798 imagens) e à limitação da GPU T4 do Colab gratuito. Em uma GPU mais potente (como A100 ou V100), o treinamento seria consideravelmente mais rápido.
:::

---

## Resultados do Treinamento

### Evolução das Métricas por Época

| Época | box_loss | cls_loss | dfl_loss | Precision | Recall | mAP50 | mAP50-95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1/5 | 1.186 | 0.8861 | 1.122 | 0.961 | 0.920 | 0.948 | 0.611 |
| 2/5 | 1.144 | 0.6005 | 1.120 | 0.985 | 0.927 | 0.964 | 0.660 |
| 3/5 | 1.101 | 0.5490 | 1.100 | 0.987 | 0.940 | 0.970 | 0.680 |
| 4/5 | 1.051 | 0.4941 | 1.075 | 0.983 | 0.950 | 0.971 | 0.681 |
| **5/5** | **1.003** | **0.4482** | **1.051** | **0.992** | **0.948** | **0.970** | **0.681** |

### Métricas Finais (best.pt)

| Métrica | Valor | Significado |
| --- | --- | --- |
| **Precision** | 0.992 (99.2%) | De todas as detecções feitas, 99.2% eram placas reais |
| **Recall** | 0.948 (94.8%) | De todas as placas existentes, 94.8% foram encontradas |
| **mAP50** | 0.970 (97.0%) | Precisão média com IoU ≥ 50% |
| **mAP50-95** | 0.681 (68.1%) | Precisão média com IoU de 50% a 95% |

### Velocidade de Inferência (GPU Tesla T4)

| Etapa | Tempo por imagem |
| --- | --- |
| Pré-processamento | 0.2 ms |
| Inferência | 2.0 ms |
| Pós-processamento | 1.8 ms |
| **Total** | **~4.0 ms** (~250 FPS teórico) |

### Análise dos Resultados Não Aparentes

&emsp;Os números acima indicam um modelo com ótima capacidade de detecção, mas alguns pontos merecem atenção:

1. **A queda de classificação (cls_loss)** foi a mais expressiva ao longo das épocas, caindo de 0.886 para 0.448. Isso mostra que o modelo aprendeu rapidamente a distinguir o que é placa do que não é, o que é esperado dado que o dataset possui apenas 1 classe.

2. **O mAP50-95 estabilizou em 0.681** a partir da época 3 e não subiu mais. Essa métrica é sensível à precisão da localização da bounding box, e sugere que 5 épocas podem não ser suficientes para refinar a localização ao máximo. Mais épocas ou ajustes de *learning rate* poderiam melhorar esse número.

3. **O Precision (99.2%) é excepcionalmente alto**, indicando que o modelo quase nunca gera falsos positivos. Isso é ideal para a aplicação de reconhecimento veicular, onde um alarme falso tem custo operacional.

4. **O Recall (94.8%) indica que ~5% das placas são perdidas**. Em cenários reais, como captura por drone em movimento, essa taxa pode aumentar devido a blur, ângulo oblíquo e distância.

---

## Comparação: YOLO11n vs. YOLOv8n

&emsp;Ambos os modelos foram treinados com os **mesmos parâmetros** (5 épocas, batch=16, imgsz=640, mesmo dataset), o que permite uma comparação direta das métricas de treinamento.

| Aspecto | YOLOv8n (V1) | YOLO11n (V2) | Vantagem |
| --- | --- | --- | --- |
| **Parâmetros** | ~3.2M | ~2.59M | ✅ YOLO11 (20% menor) |
| **GFLOPs** | ~8.7 | 6.4 | ✅ YOLO11 (26% mais leve) |
| **Tamanho do peso** | ~6 MB | 5.5 MB | ✅ YOLO11 |
| **Tempo de inferência** | ~2.5 ms | 2.0 ms | ✅ YOLO11 (20% mais rápido) |
| **Camadas** | ~168 | 182 | Empate (mais camadas, porém mais leves) |
| **Blocos de atenção** | Não | Sim (C2PSA) | ✅ YOLO11 |
| **mAP50 (estimado)** | ~0.96 | 0.970 | ✅ YOLO11 (levemente superior) |

&emsp;As métricas de treinamento e benchmark **indicam que o YOLO11n tem potencial para superar o YOLOv8n** em todos os aspectos medidos: é mais leve, mais rápido e apresenta mAP levemente superior. No entanto, esses são resultados de benchmark em dataset controlado. A confirmação em cenário real, com a câmera do drone, condições de iluminação variáveis e movimentação ainda **não foi possível nesta sprint**, conforme detalhado na seção seguinte.

:::note
Os números de treinamento são promissores e há **indícios claros** de que o YOLO11n é uma evolução em relação ao YOLOv8n. Porém, a validação definitiva depende de testes práticos com o drone, que serão realizados na Sprint 4.
:::

---

## Teste de Execução Local

&emsp;Após o treinamento no Colab, o modelo `license_plate_best.pt` foi integrado ao pipeline existente e testado localmente com o drone DJI Tello. O código de inferência (`plate_recognizer.py`) foi atualizado para utilizar os novos pesos do YOLO11.

:::warning
Durante esta sprint, **foi possível realizar apenas um teste prático** com a câmera do drone, devido à limitação de tempo. Esse único teste apresentou **delay severo** no stream de vídeo, o que impediu a validação real do desempenho do YOLO11 em cenário operacional. As conclusões sobre a superioridade do modelo são baseadas nas métricas de treinamento, e não em testes de campo conclusivos.
:::

### Problemas Encontrados

&emsp;Durante a execução local do `drone.py` na branch `feat/yoloV11`, foram identificados dois problemas recorrentes:

#### 1. Erro de rede (`urlopen error`)

&emsp;O terminal exibiu repetidamente a mensagem:

```
Erro ao processar frame: <urlopen error [Errno 11001] getaddrinfo failed>
```

&emsp;Esse erro indica que o EasyOCR tentava baixar o modelo de detecção de texto na primeira execução, mas a conexão de rede falhava, possivelmente porque o computador estava conectado à rede Wi-Fi do drone (que não possui acesso à internet). O sistema entrava em um loop de tentativas de download, como mostrado na imagem abaixo:

<div align="center">
    <sup>Figura 1: Terminal com erros repetidos de rede durante a tentativa de download do modelo EasyOCR</sup>
    <img src="/img/sprint-3/visao-computacional/yolo11.png" />
    <sup>Fonte: Autoria própria (2026).</sup>
</div>

#### 2. Mensagem "Using CPU"

&emsp;O terminal exibiu consistentemente:

```
Using CPU. Note: This module is much faster with a GPU.
```

&emsp;Isso confirma que a inferência local estava sendo executada em CPU, sem aceleração por GPU. No caso do YOLO11, a inferência em CPU é significativamente mais lenta que em GPU, enquanto no Colab o modelo fazia inferência em **2.0 ms por imagem** com a Tesla T4, em CPU local o tempo pode subir para **50-200 ms por imagem**, gerando atraso perceptível no stream do drone.

#### 3. Download com progresso

&emsp;Quando o download do modelo EasyOCR eventualmente teve sucesso, o terminal mostrou barras de progresso até 100%, seguido da mensagem "Aguardando imagem do drone...", indicando que o pipeline de vídeo aguardava a conexão com o drone:

<div align="center">
    <sup>Figura 2: Terminal com download do modelo e início da captura de vídeo</sup>
    <img src="/img/sprint-3/visao-computacional/yolo11-2.png" />
    <sup>Fonte: Autoria própria (2026).</sup>
</div>

### Análise dos Problemas

| Problema | Causa | Impacto | Solução proposta |
| --- | --- | --- | --- |
| Loop de download | Wi-Fi do drone sem internet | OCR não carrega, detecção não funciona | Pré-baixar o modelo antes de conectar ao drone |
| Inferência em CPU | Máquina local sem GPU CUDA | Latência alta (~50-200ms vs. 2ms) | Usar GPU ou reduzir frequência de detecção |
| Mensagens repetidas | Exceção capturada mas sem controle de retry | Polui o terminal, dificulta debug | Implementar retry com limite e backoff |

---


## Conclusão

&emsp;O teste do YOLO11n trouxe **indícios positivos** de que o modelo representa uma evolução em relação ao YOLOv8n. Com **99.2% de precision**, **94.8% de recall** e **mAP50 de 97.0%** no treinamento, as métricas de benchmark superaram o modelo anterior, sendo ao mesmo tempo **mais leve** (20% menos parâmetros) e **mais rápido** (2.0 ms de inferência em GPU). A arquitetura aprimorada com blocos de atenção C2PSA demonstrou potencial para obter melhor precisão com menor custo computacional.

&emsp;No entanto, **não é possível afirmar com certeza que o YOLO11 é melhor para o nosso caso de uso real**. O único teste prático realizado com a câmera do drone apresentou delay severo no stream de vídeo, impossibilitando a análise de desempenho em condições reais de operação. Os problemas de rede (Wi-Fi do drone sem internet), a execução em CPU e o tempo insuficiente para repetir os testes impediram uma validação conclusiva.

&emsp;O treinamento demandou **~2 horas e 40 minutos** no Colab — um tempo significativo que reforça a importância de planejar os experimentos e preservar os pesos treinados. A execução local expôs fragilidades no gerenciamento de dependências do EasyOCR (download do modelo dependente de internet) e na queda de performance ao rodar sem GPU.

&emsp;Em resumo: os números do YOLO11n são promissores, mas ainda depende dos **testes de campo** planejados para a Sprint 4.

---

## Referências

- Ultralytics YOLO11 — [https://docs.ultralytics.com/models/yolo11/](https://docs.ultralytics.com/models/yolo11/)
- Dataset utilizado — [License Plate Recognition (Roboflow Universe)](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e)
- Notebook de treinamento — [Google Colab](https://colab.research.google.com/drive/1VPsfnulhuLGSF7wmTR4U6nLj9nvZL34S?usp=sharing)
- Documentação da V1 (YOLOv8n) — [Modelo de Classificação V1](../sprint-2/Visão%20Computacional/analise-tecnica-pipeline-placas)
