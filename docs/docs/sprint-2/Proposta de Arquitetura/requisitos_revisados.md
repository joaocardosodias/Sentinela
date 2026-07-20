---
sidebar_position: 2
title: Requisitos Revisados
---

# Requisitos Revisados

## Contexto

&emsp;Este documento apresenta a versão revisada dos requisitos do sistema, elaborada a partir do feedback recebido na avaliação da Sprint 1. As correções abordam quatro pontos: **redundância entre metas de tempo**, **métricas pouco justificadas**, **uso impreciso de terminologia** e **um requisito de GPS incompatível com o drone** Tello utilizado no protótipo - que não possui e não terá módulo GPS.

---

## Alterações em Relação à Sprint 1

### RF-03 - GPS removido

&emsp;O requisito original exigia que o sistema associasse coordenadas GPS da telemetria do drone a cada placa identificada. Como não temos GPS, esse requisito foi reescrito como "Registro Temporal e de Zona de Operação": o sistema passa a associar o horário e a zona de operação da missão a cada detecção.

### RNF-06 - Removido

&emsp;O requisito de precisão GPS (erro radial máximo de 5 metros) foi removido integralmente, pois não há módulo GPS no drone e nao usaremos em nosso MVP.

### RNF-01, RNF-02 e RNF-03 - Redundância resolvida

&emsp;Os três requisitos usavam o mesmo limite de 5 segundos para etapas diferentes do mesmo pipeline, tornando-os redundantes entre si:

- RNF-01 (consulta + alerta em até 5s) e RNF-02 (verificação de match em menos de 5s) se sobrepunham completamente. RNF-02 foi removido.
- RNF-01 foi consolidado como limite fim a fim do pipeline (captura → alerta em 5s).
- RNF-03 foi mantido como sub-limite de notificação, mas com valor ajustado para 2 segundos, justificando sua existência como requisito separado.

### RNF-05 - "confiabilidade" modificado para "acurácia"

&emsp;O requisito pretendia medir a taxa de leituras corretas do modelo, que é acurácia. O termo foi só corrigido.

---

## Requisitos Funcionais

### RF-01 - Captura de Imagem

&emsp;O sistema deve ser capaz de capturar imagens nítidas de placas de veículos estacionados e em movimento através da câmera do drone.

### RF-02 - Visão Computacional

&emsp;O sistema deve extrair os caracteres alfanuméricos das placas capturadas nas imagens recebidas do drone, utilizando visão computacional.

### RF-03 - Registro Temporal e de Zona de Operação

&emsp;O sistema deve associar automaticamente o horário (Date Time) e a zona de operação definida para a missão ao registro de cada placa identificada, permitindo rastrear quando e em qual área o veículo foi detectado.

### RF-04 - Consulta de Sinistros

&emsp;O sistema deve realizar uma chamada automática à API da Pier para verificar o status de roubo ou furto da placa capturada.

### RF-05 - Notificação de Match

&emsp;Caso a placa conste na base de sinistros, o sistema deve gerar um alerta imediato contendo a placa, a zona de operação e o Date Time de onde o veículo foi identificado.

### RF-06 - Health Check

&emsp;O sistema deve garantir que os drones estão conectados e enviando dados da operação.

---

## Requisitos Não Funcionais

### RNF-01 - Tempo de Resposta do Pipeline

&emsp;O pipeline completo - desde a captura da imagem até a geração do alerta - deve ser concluído em até 5 segundos, evitando que a defasagem de informação comprometa a utilidade operacional em campo.

### RNF-02 - Latência de Alerta Crítico

&emsp;Uma vez detectado um *match* positivo, o sistema deve disparar a notificação para o frontend e encaminhá-la à Pier em menos de 2 segundos, aproveitando a janela de probabilidade de recuperação antes que o veículo deixe o local.

### RNF-03 - Latência de Vídeo no Dashboard

&emsp;O vídeo exibido no dashboard do gestor da operação deve apresentar uma latência inferior a 5 segundos, garantindo que as decisões operacionais sejam tomadas com base em imagens próximas ao tempo real.

### RNF-04 - Acurácia do Modelo

&emsp;O modelo deve atingir acurácia mínima de 80% na leitura de placas em condições de operação normais, assegurando a qualidade das detecções realizadas em voo.

### RNF-05 - Health Check

&emsp;A garantia de conectividade dos drones deve ser feita a partir das informações de telemetria enviadas pelo próprio drone, sem depender de mecanismos externos de verificação.
