---
sidebar_position: 1
title: Sprint 4
---

# Sprint 4

 Documentação referente à Sprint 4 do projeto. Nesta organização, as ações realizadas entre **1 e 12 de junho de 2026** pertencem à Sprint 4.

## Objetivos

- consolidar a camada de OCR para uso em câmera real;
- simplificar a arquitetura do processamento de imagem voltada à leitura de placas;
- reduzir código legado e wrappers antigos;
- instrumentar o runtime com métricas para avaliar custo, seletividade e estabilidade.

## Entregas

- reorganização da camada `src/visao_computacional/ocr/` em módulos coesos;
- remoção da antiga árvore `image_processing/` e de wrappers legados não utilizados;
- pipeline de OCR em runtime com quality gate, cooldown e estabilização temporal;
- documentação técnica da Sprint 4 com comparação entre pipeline anterior e atual;
- captura visual do antes e depois da ROI usada no OCR.

## Artefatos

- [Processamento de Imagem e OCR de Placas](./Visão%20Computacional/processamento-imagem-ocr)
