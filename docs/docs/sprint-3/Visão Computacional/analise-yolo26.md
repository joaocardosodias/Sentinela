---
sidebar_position: 2
title: Modelo de Classificação - YOLO26
---

# Evolução do Modelo de Visão Computacional: YOLOv8n → YOLO26

&emsp;Durante o desenvolvimento do sistema de reconhecimento automático de placas veiculares (ALPR) integrado ao drone DJI Tello, foram identificados problemas relacionados à fluidez do processamento em tempo real, estabilidade do reconhecimento e desempenho do OCR em determinadas condições de captura.

&emsp;Na versão inicial do projeto, o pipeline utilizava o modelo **`YOLOv8n`** para detecção de placas veiculares. Embora o modelo tenha apresentado resultados satisfatórios para validação inicial do fluxo de visão computacional, os testes realizados em ambiente real evidenciaram limitações relacionadas à latência, travamentos ocasionais durante o processamento dos frames e inconsistências na extração dos caracteres das placas.

&emsp;Com o objetivo de melhorar o desempenho geral do pipeline, foi realizada uma migração experimental para o modelo **`YOLO26`**,  disponibilizado pela Ultralytics e otimizado para cenários de inferência em tempo real e dispositivos com recursos computacionais limitados.

&emsp;A principal proposta da migração não era apenas aumentar a precisão da detecção das placas, mas também reduzir o custo computacional da inferência, melhorar a estabilidade visual da aplicação durante o streaming do drone e avaliar possíveis impactos positivos indiretos na etapa de OCR.

&emsp;Os testes realizados compararam o comportamento do pipeline utilizando os dois modelos em diferentes cenários:

* execução em tempo real com o drone DJI Tello;
* imagens estáticas em condições ideais;
* reconhecimento de múltiplas placas simultaneamente;
* variações de distância, inclinação e qualidade visual das placas.

&emsp;A partir desses experimentos, foi possível observar melhorias perceptíveis relacionadas à fluidez do sistema e à velocidade de reconhecimento utilizando o YOLO26. Entretanto, também foram identificadas limitações persistentes principalmente na etapa de OCR, indicando que parte significativa dos erros atuais provavelmente não está mais relacionada apenas ao detector de objetos, mas também ao conjunto de treinamento, pré-processamento das imagens e motor de reconhecimento óptico utilizado no pipeline.

---

## Diferenças Arquiteturais entre YOLOv8n e YOLO26

&emsp;O modelo **`YOLOv8n`** foi inicialmente escolhido por ser uma versão compacta da família YOLO, permitindo inferência relativamente rápida mesmo em dispositivos com limitações computacionais. A arquitetura utiliza uma abordagem *anchor-free* e blocos convolucionais otimizados, sendo adequada para aplicações em tempo real.

&emsp;Entretanto, durante os testes com o drone DJI Tello, foram observados alguns comportamentos indesejados:

* atraso perceptível entre o movimento do drone e a renderização da detecção;
* engasgos (*stuttering*) no fluxo de vídeo;
* acúmulo de frames no buffer;
* maior instabilidade das bounding boxes;
* maior tempo para reconhecimento completo da placa.

&emsp;Para reduzir esses problemas, foi realizado um processo de migração para o modelo **`YOLO26`**.

&emsp;Segundo a documentação oficial da Ultralytics, o `YOLO26` foi desenvolvido com foco em eficiência computacional, baixa latência e aplicações em dispositivos de borda (*edge computing*), buscando reduzir o custo de inferência sem comprometer significativamente a capacidade de detecção.

<div align="center">    
    <sup>Figura 1: Comparação entre YOLOv8n e YOLO26 </sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780016537/26c0c4b6-548e-4200-a74e-051a4119825a.png" />
    <sup>Fonte: Ultralytics. Acesso em: https://docs.ultralytics.com/pt/models/yolo26#vis%C3%A3o-geral </sup>
</div>


Durante os testes realizados, o YOLO26 apresentou:

* menor latência de inferência;
* menor travamento do fluxo de vídeo;
* menor acúmulo de frames atrasados;
* maior fluidez visual;
* maior estabilidade das bounding boxes;
* reconhecimento perceptivelmente mais rápido.

&emsp;Além disso, o modelo demonstrou maior consistência ao detectar placas em movimento e em cenários com múltiplas placas simultaneamente.


### Configuração de Treinamento Utilizada

&emsp;Para garantir uma comparação mais consistente entre os modelos, o treinamento do YOLO26 foi realizado seguindo parâmetros semelhantes aos utilizados anteriormente no treinamento do YOLOv8n.

&emsp;Dessa forma, buscou-se reduzir a influência de variáveis externas no processo comparativo, permitindo observar com maior clareza os impactos específicos da mudança arquitetural entre os modelos.

O processo de *fine-tuning* manteve a mesma proposta geral utilizada anteriormente:

* utilização do mesmo conjunto base de treinamento;
* mesma tarefa de detecção de placas;
* mesma estrutura geral do pipeline;
* mesmas etapas posteriores de OCR e validação por Regex.

&emsp;Essa padronização foi importante para permitir uma análise mais isolada da troca do detector, reduzindo a possibilidade de que diferenças observadas fossem consequência apenas de alterações no treinamento.

&emsp;Mesmo utilizando uma estratégia semelhante de treinamento entre os modelos, alguns padrões de erro permaneceram presentes durante os testes, principalmente na etapa de OCR. Esse comportamento indicou que parte significativa das limitações atuais do sistema pode não estar relacionada apenas ao detector, mas também ao reconhecimento óptico e às características do conjunto de treinamento utilizado.

&emsp;Esse comportamento reforçou a hipótese de que parte significativa das falhas atuais do sistema provavelmente está relacionada:

* ao conjunto de treinamento utilizado;
* à diversidade limitada de exemplos;
* à ausência de imagens com inclinações e condições adversas;
* ao pré-processamento da ROI;
* ou ao próprio mecanismo de OCR empregado no pipeline.


---

## Estrutura do Pipeline de Reconhecimento

&emsp;O pipeline atual de visão computacional opera em duas etapas principais:

1. **Detecção da placa**

   * realizada utilizando YOLO;
   * responsável por localizar a posição da placa no frame;
   * retorna bounding boxes e confiança da detecção.

2. **Reconhecimento óptico de caracteres (OCR)**

   * realizado utilizando EasyOCR;
   * responsável por extrair os caracteres da região recortada;
   * aplica validação por Regex para formatos brasileiros.

O fluxo geral do sistema funciona da seguinte forma:

```text
[Fluxo de Vídeo Drone Tello] 
             │
             ▼
┌───────────────────────────┐      Substituído por:      ┌───────────────────────────┐
│     YOLOv8n (Baseline)    │   ───────────────────────> │          YOLO26           │
│  - Alta Latência em Edge  │                            │  - Baixo Overhead de Memo │
│  - Flutuação de Bounding  │                            │  - Inferência Ultra-Fluida│
└───────────────────────────┘                            └───────────────────────────┘
             │
             ▼
┌───────────────────────────┐
│   Recorte de ROI (Crop)   │
└───────────────────────────┘
             │
             ▼
┌───────────────────────────┐
│     Pipeline EasyOCR      │ ---> [Gargalo de Processamento Semântico]
└───────────────────────────┘
```

Os padrões brasileiros suportados atualmente são:

* modelo antigo: `LLLNNNN`
* modelo Mercosul: `LLLNLNN`

Além disso, o sistema realiza correções automáticas de homóglifos frequentemente confundidos pelo OCR:

* `B ↔ 8`
* `I ↔ 1`
* `O ↔ 0`
* `S ↔ 5`

---

## Metodologia Experimental

&emsp;Com o objetivo de entender a origem dos erros observados no reconhecimento das placas, os testes foram divididos em dois cenários distintos:

1. **testes em condições perfeitas**
2. **testes em ambiente real utilizando o drone**

O objetivo era isolar variáveis e identificar se os problemas estavam relacionados:

* à qualidade da câmera do drone;
* ao streaming UDP;
* à movimentação do drone;
* ao modelo YOLO;
* ao OCR;
* ao conjunto de treinamento utilizado.



### 1. Testes em Condições Perfeitas

&emsp;Nos testes em condições perfeitas, imagens estáticas foram carregadas diretamente no pipeline utilizando `cv2.imread`, eliminando:

* compressão do streaming;
* movimentação do drone;
* delay de transmissão;
* instabilidade da câmera;
* perda de qualidade causada pelo vídeo em tempo real.

Para isso, foi realizada uma alteração temporária no `__main__` do arquivo `plate_recognizer.py`.

O código utilizado foi:

```python
if __name__ == "__main__":

    image_path = "placas.jpg"

    frame = cv2.imread(image_path)

    if frame is None:
        raise RuntimeError("Nao foi possivel carregar a imagem.")

    frame, frame_results = process_frame(frame)

    print(frame_results)

    cv2.imshow("Resultado", frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
```

&emsp;Nesse cenário, foi possível avaliar o comportamento do pipeline em condições ideais de processamento.

Os testes mostraram que:

* o YOLO26 detectou corretamente a existência da placa em praticamente todos os cenários;
* os principais erros permaneceram concentrados na etapa de OCR.

&emsp;Isso foi um resultado importante, pois indicou que a detecção da placa não era mais o principal problema do sistema.

---

### 2. Testes em Ambiente Real com Drone

&emsp;Após os testes estáticos, foram realizados testes utilizando o streaming em tempo real do drone DJI Tello.

Nesse cenário, o sistema precisava lidar simultaneamente com:

* movimentação da câmera;
* compressão do vídeo;
* delay do streaming;
* variações de iluminação;
* borrões de movimento;
* vibração do drone;
* inclinação das placas;
* mudanças rápidas de distância.

O objetivo era avaliar o comportamento do pipeline em condições próximas do uso real do sistema.

---

## Resultados Experimentais

### 1. Resultados em Condições Perfeitas

&emsp;Nos testes com imagens estáticas, foi observado que a detecção da placa ocorreu corretamente em praticamente todos os testes, e os erros ocorreram principalmente durante a extração dos caracteres. Foi possível identificar padrões recorrentes de erro.


#### Troca do caractere “B” por “8”

<div align="center">    
    <sup>Figura 2: Janela de vídeo com a placa reconhecida</sup>
    <img src=" https://res.cloudinary.com/dwewomj84/image/upload/v1780003634/Captura_de_tela_de_2026-05-28_15-13-44-1_qhtjyf.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>


&emsp;A placa correta é `ABC1B34`, porém o OCR retornou `ABC1834`, confundindo o caractere `B` com `8`. Nesse caso, a placa apresentava uma leve inclinação. Mesmo sendo pequena, a inclinação influenciou negativamente o reconhecimento dos caracteres.



#### Reconhecimento correto em condição ideal

<div align="center">    
    <sup>Figura 3: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780003634/Captura_de_tela_de_2026-05-28_15-01-57_cdme8u.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>


&emsp;Reconhecimento correto da placa `BRA3R52` em uma imagem mais reta e com maior nitidez. Esse comportamento foi recorrente durante os testes: placas alinhadas frontalmente apresentaram maior taxa de sucesso no OCR.


#### Detecção sem extração de caracteres

<div align="center">    
    <sup>Figura 4: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780003634/Captura_de_tela_de_2026-05-28_15-04-39_ye7aqz.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>

&emsp;O sistema detectou corretamente a existência da placa, porém o OCR não conseguiu extrair os caracteres. Mesmo com uma inclinação muito pequena, o OCR falhou completamente na leitura textual.


#### Falha de OCR em placas mais distantes

<div align="center">    
    <sup>Figura 5: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780003635/Captura_de_tela_de_2026-05-28_14-56-00_lkyomf.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>

&emsp;A placa foi detectada corretamente, porém os caracteres não foram reconhecidos devido à distância da câmera. Esse comportamento mostrou que o OCR possui forte dependência da resolução efetiva da ROI recortada.


#### Confusão entre caracteres semelhantes

<div align="center">    
    <sup>Figura 6: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780003635/Captura_de_tela_de_2026-05-28_15-00-34_vm49fd.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>

&emsp;A placa correta é `LSU3J43`, porém o OCR retornou `LSU3J45`, confundindo os caracteres `3` e `5`.

---

### 2. Resultados com o Drone

&emsp;Nos testes em tempo real utilizando o drone, os padrões observados nos testes estáticos continuaram aparecendo, porém de forma intensificada devido às limitações físicas do ambiente.

Foi observado:

* pequeno delay entre mostrar a placa e o reconhecimento aparecer;
* maior dificuldade com placas distantes;
* sensibilidade elevada à movimentação;
* oscilações na leitura dos caracteres;
* maior taxa de erro quando a imagem estava inclinada.



#### Reconhecimento correto com alta estabilidade

<div align="center">    
    <sup>Figura 7: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780003630/Captura_de_tela_de_2026-05-28_17-12-02_qgovno.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>

&emsp;Reconhecimento correto da placa `BRA2E19` utilizando o drone. Nesse cenário, observou-se que manter a placa estável por mais tempo aumentava a confiabilidade do reconhecimento.


#### Confusão causada por movimentação

<div align="center">    
    <sup>Figura 8: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780003631/Captura_de_tela_de_2026-05-28_17-14-51_sfghei.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>


&emsp;A placa correta `DOK2A20` foi interpretada como `OOK2A20`, indicando confusão entre `D` e `O`.


#### Reconhecimento simultâneo de múltiplas placas

<div align="center">    
    <sup>Figura 9: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780003630/Captura_de_tela_de_2026-05-28_17-35-22_faiaz0.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>


&emsp;O sistema conseguiu detectar e reconhecer simultaneamente duas placas no mesmo frame. Esse resultado mostrou boa capacidade do detector YOLO26 em cenários multialvo.


#### Reconhecimento parcial em placa distante

<div align="center">    
    <sup>Figura 10: Janela de vídeo com a placa reconhecida</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1780003630/Captura_de_tela_de_2026-05-28_17-04-43_tcgbon.png" />
    <sup>Fonte: Autoria própria (2026). </sup>
</div>

&emsp;A placa correta era `LSN4I49`, porém o OCR retornou `LSN4149`, confundindo `I` com `1`.

---

## Padrões de Erro Identificados

&emsp;A análise experimental permitiu identificar padrões recorrentes de falha.

| Padrão de erro                           | Causa provável                       | Exemplo observado                         |
| ---------------------------------------- | ------------------------------------ | ----------------------------------------- |
| Troca entre letras e números semelhantes | Similaridade visual entre caracteres | `B ↔ 8`, `I ↔ 1`, `3 ↔ 5`                 |
| Falha em placas inclinadas               | Ausência de correção geométrica      | OCR falhando mesmo com pequena rotação    |
| Falha em placas distantes                | ROI com poucos pixels úteis          | Bounding box detectada sem texto          |
| Delay no reconhecimento                  | Tempo de processamento do OCR        | Reconhecimento aparecendo segundos depois |
| Oscilação de leitura                     | Movimento do drone                   | Caracteres mudando entre frames           |

&emsp;Foi possível perceber que muitos erros ocorreram de forma consistente tanto nos testes perfeitos quanto nos testes com drone.

&emsp;Isso reforçou a hipótese de que parte significativa das falhas não está relacionada apenas à câmera do drone, mas sim:

* ao processo de treinamento;
* ao conjunto de dados utilizado;
* ao OCR;
* à ausência de correções geométricas antes da leitura textual.


### Análise sobre o Confidence Score

&emsp;Durante os testes, foi observado que o valor de confiança exibido pelo sistema nem sempre refletia a correção dos caracteres reconhecidos.

Isso ocorre porque o valor:

```python
conf = float(box.conf.item())
```

representa apenas a confiança do YOLO na detecção da existência da placa dentro da bounding box.

Ou seja:

* a confiança alta significa que o YOLO acredita que existe uma placa naquela região;
* isso não significa que o OCR leu corretamente os caracteres.

&emsp;Em diversos testes, placas parcialmente incorretas ainda apresentavam valores altos de confiança, como `0.76` ou `0.80`. Portanto, a confiabilidade da detecção não deve ser confundida com a confiabilidade da leitura textual.

---

## Hipóteses Técnicas

&emsp;A partir dos resultados experimentais, foram levantadas algumas hipóteses para explicar os problemas persistentes observados.

### Problemas relacionados ao OCR

&emsp;O EasyOCR demonstrou dificuldade em:

* placas inclinadas;
* baixa resolução;
* sombras;
* distâncias maiores;
* pequenas rotações;
* caracteres visualmente semelhantes.

&emsp;Além disso, o EasyOCR é um OCR genérico para textos de cena e não especializado especificamente em placas brasileiras.



### Possíveis problemas no treinamento

&emsp;Como erros semelhantes ocorreram tanto no YOLOv8n quanto no YOLO26, existe uma forte hipótese de que parte do problema esteja:

* no conjunto de treinamento utilizado;
* na quantidade de imagens;
* na diversidade das imagens;
* na qualidade das anotações;
* na quantidade de exemplos inclinados;
* na ausência de exemplos mais difíceis durante o treinamento.


### Ausência de correção geométrica

&emsp;O pipeline atual não realiza:

* correção de perspectiva;
* alinhamento da placa;
* retificação geométrica.

&emsp;Isso faz com que pequenas inclinações influenciem excessivamente o OCR.

---

## Melhorias Futuras

&emsp;Como próximos passos do projeto, pretende-se investigar:

* melhoria do dataset de treinamento;
* aumento do número de épocas;
* treinamento com imagens mais difíceis;
* testes com outros modelos OCR;
* substituição do EasyOCR por PaddleOCR;
* aplicação de correção de perspectiva;
* uso de super-resolução para placas distantes;
* implementação de rastreamento temporal mais robusto;
* melhoria do sistema de confiança;
* análise quantitativa de taxa de erro por caractere.

&emsp;Apesar das limitações observadas, os resultados mostraram que a migração para o YOLO26 foi positiva para o projeto, principalmente em relação à fluidez do sistema, velocidade de inferência e estabilidade visual do pipeline.

---

## Referências 

ULTRALYTICS. **YOLO26**. Disponível em: https://docs.ultralytics.com/pt/models/yolo26/. Acesso em: 28 mai. 2026.

ULTRALYTICS. **Ultralytics YOLO Documentation**. Disponível em: https://docs.ultralytics.com/. Acesso em: 28 mai. 2026.

JAIDED AI. **EasyOCR Documentation**. Disponível em: https://www.jaided.ai/easyocr/. Acesso em: 28 mai. 2026.

OPENCV. **OpenCV Documentation**. Disponível em: https://opencv.org/. Acesso em: 28 mai. 2026.
