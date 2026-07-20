---
sidebar_position: 2
title: Comparativo EasyOCR vs PaddleOCR
---

# Comparativo dos Modelos: EasyOCR vs PaddleOCR

Este documento registra o experimento realizado para comparar o EasyOCR, que ja era
usado no pipeline de leitura de placas, com o PaddleOCR, avaliado como uma
possivel alternativa local para melhorar o reconhecimento dos caracteres.

O objetivo do teste nao foi alterar o detector de placas. O YOLO26 continuou
responsavel por localizar a placa no frame, enquanto o OCR recebeu apenas o
recorte da placa (`plate_crop`). Dessa forma, a comparacao ficou concentrada na
etapa de leitura textual.

## Contexto

O pipeline ativo de visao computacional esta no arquivo
`src/visao_computacional/yolo26/plate_recognizer.py`.

Antes do experimento, o fluxo principal era:

1. Capturar frame do drone.
2. Detectar a placa com YOLO26.
3. Recortar a regiao da placa.
4. Aplicar pre-processamento com OpenCV.
5. Ler os caracteres com EasyOCR.
6. Corrigir confusoes comuns por posicao da placa.
7. Validar o texto com regex de placa antiga brasileira, Mercosul e fallback UK.

O PaddleOCR foi integrado para responder a seguinte pergunta:

> Trocar o EasyOCR pelo PaddleOCR melhora o resultado final da leitura de placas?

## Implementacao Do Experimento

Foi mantida uma camada comum de validacao para os dois OCRs. Isso significa que
EasyOCR e PaddleOCR passam pelas mesmas regras:

- limpeza do texto;
- remocao de espacos, hifens e caracteres invalidos;
- correcao de caracteres visualmente parecidos, como `I/1`, `O/0` e `B/8`;
- validacao por regex para placas brasileiras antigas e Mercosul;
- retorno padronizado com `plate`, `format`, `raw_text`, `valid` e `ocr_source`.

Foram criados tres modos de execucao:

```env
OCR_PROVIDER=easyocr
OCR_PROVIDER=paddle
OCR_PROVIDER=compare
```

O modo `compare` executa EasyOCR e PaddleOCR no mesmo recorte de placa e retorna
um campo adicional `ocr_comparison`, permitindo inspecionar o resultado bruto dos
dois modelos.

Depois da comparacao, o projeto voltou a usar EasyOCR como padrao:

```env
OCR_PROVIDER=easyocr
OCR_COMPARE_PRIMARY=paddle
```

## Benchmark Criado

Tambem foi criado o script:

```text
src/visao_computacional/benchmark_ocr.py
```

Ele recebe uma imagem ou pasta com recortes de placas e executa os dois OCRs nos
mesmos arquivos.

Comando de exemplo:

```bash
python -m src.visao_computacional.benchmark_ocr recortes_placas --output resultados_ocr.csv --json-summary
```

O CSV gerado possui as seguintes colunas:

| Coluna | Descricao |
| --- | --- |
| `image` | Caminho da imagem testada |
| `provider` | OCR utilizado: `easyocr` ou `paddleocr` |
| `latency_ms` | Tempo de execucao em milissegundos |
| `plate` | Placa final depois das regras de correcao e validacao |
| `format` | Formato reconhecido, como `BR_MERCOSUL` |
| `raw_text` | Texto bruto retornado pelo OCR |
| `valid` | Indica se a leitura passou nas regras do projeto |
| `expected_plate` | Placa esperada, vinda do CSV ou do nome do arquivo |
| `match` | Indica se `plate` bateu com `expected_plate` |

Quando nao ha CSV de gabarito, o benchmark tenta inferir a placa esperada pelo
nome do arquivo. Por exemplo, `ABC1D23.png` vira o gabarito `ABC1D23`.


## Evidencia Textual Do Benchmark

Foi criada uma imagem sintetica de placa com o texto `ABC1D23`. A imagem foi
usada como recorte de placa, simulando a saida do YOLO antes da etapa de OCR.

Saida do benchmark:

```text
image,provider,latency_ms,plate,format,raw_text,valid,expected_plate,match
.ocr_tmp\ABC1D23.png,easyocr,7883.04,ABC1D23,BR_MERCOSUL,ABCID23,True,ABC1D23,True
.ocr_tmp\ABC1D23.png,paddleocr,10311.81,ABC1D23,BR_MERCOSUL,ABC1D23,True,ABC1D23,True
{
  "easyocr": {
    "total": 1,
    "valid": 1,
    "matches": 1,
    "avg_latency_ms": 7883.04
  },
  "paddleocr": {
    "total": 1,
    "valid": 1,
    "matches": 1,
    "avg_latency_ms": 10311.81
  }
}
```

Tambem foi executado um teste direto dos providers:

```text
PaddleOCR:
{'plate': 'ABC1D23', 'format': 'BR_MERCOSUL', 'raw_text': 'ABC1D23', 'valid': True, 'ocr_source': 'paddleocr'}

EasyOCR:
{'plate': 'ABC1D23', 'format': 'BR_MERCOSUL', 'raw_text': 'ABCID23', 'valid': True, 'ocr_source': 'easyocr'}
```

## Analise Dos Resultados

Os dois OCRs chegaram ao mesmo resultado final:

```text
ABC1D23
```

A diferenca apareceu no texto bruto:

| Modelo | Texto bruto | Placa final | Resultado |
| --- | --- | --- | --- |
| EasyOCR | `ABCID23` | `ABC1D23` | Correto apos regra de correcao |
| PaddleOCR | `ABC1D23` | `ABC1D23` | Correto direto no OCR |

O PaddleOCR teve uma leitura bruta melhor nesse teste sintetico, pois nao
confundiu o caractere `1` com `I`. Mesmo assim, para o sistema completo, essa
diferenca nao alterou a placa final, porque a regra de correcao existente ja
resolveu o erro do EasyOCR.

A comparacao de latencia nao deve ser interpretada como conclusiva. O teste
incluiu carregamento inicial de modelos e execucao em CPU. Para uma avaliacao de
desempenho mais precisa, seria necessario usar um conjunto maior de imagens,
descartar a primeira execucao de aquecimento e medir varias repeticoes por
imagem.

## Decisao Tecnica

A decisao final foi manter EasyOCR como OCR padrao do projeto.

Motivos:

- o resultado final foi igual ao PaddleOCR no teste realizado;
- EasyOCR ja estava integrado ao pipeline do drone;
- as regras de correcao do projeto ja compensam erros comuns do EasyOCR;
- PaddleOCR adiciona dependencias maiores e mais sensiveis ao ambiente;
- nao houve ganho suficiente no resultado final para justificar a troca.

O PaddleOCR permanece documentado e disponivel como alternativa experimental
para comparacoes futuras.


