---
sidebar_position: 3
title: Banco de Dados
---

# Banco de Dados

&emsp; Esta documentação detalha a arquitetura, as decisões de modelagem e o fluxo de dados do sistema de recuperação de veículos, unificando a base de sinistros da Pier com os dados operacionais dos drones.

## Passo 1 - Decisão Arquitetônica (Simplificação)

&emsp; Inicialmente, o grupo considerou o uso de múltiplas tabelas associativas para interligar usuários, drones e scans. No entanto, visando a performance em tempo real e a facilidade de integração com o Supabase, optamos por uma arquitetura relacional mais direta. 

&emsp; Decidimos unificar os bancos de dados da empresa (veículos roubados) e da operação em um único esquema. Isso permite que a consulta entre uma placa escaneada e a base de sinistros ocorra em milissegundos, garantindo que o alerta chegue ao Gestor Pier quase instantaneamente.

## Passo 2 - Estrutura das Tabelas (ERD)

&emsp; O banco de dados foi estruturado em tabelas principais, utilizando **UUIDs** como chaves primárias para garantir a segurança e a unicidade dos registros no ambiente de nuvem:

* **usuario:** Gerencia o acesso ao sistema e define se o usuário é um Gestor de Campo ou um Analista da Pier.
* **veiculos:** Simula a base de dados da Pier com placas, modelos e o status de roubo.
* **operacoes:** Registra os dados macro de cada missão, representando a **zona de operação** referenciada no RF-03.
* **drones:** Armazena dados cadastrais e operacionais do drone, como bateria, conectividade e status de voo. O schema ainda preserva campos de latitude/longitude por compatibilidade de evolução, mas eles não são requisito do MVP.
* **scans:** A tabela central que registra cada leitura de placa, o link para a foto e o `horario_scan` — campo que implementa o **Registro Temporal** exigido pelo RF-03 revisado.
* **veiculos_scans / usuarios_scans:** Tabelas de conexão que permitem a rastreabilidade total (quem validou qual alerta).

## Passo 3 - Fluxo de Validação e Log de Dados

&emsp; Um dos maiores desafios foi garantir que o sistema não perdesse informações em caso de erro humano ou falso positivo da IA. Para isso, implementamos um fluxo de "Validação Humana":

- 1. O drone identifica uma placa e envia para a tabela `scans` com o status **'pendente'**.
- 2. O Analista da Pier visualiza a foto e decide se o alerta é real.
- 3. Em vez de deletar o registro caso seja um falso positivo, o sistema realiza um **UPDATE** para o status **'rejeitado'**.
- 4. O registro é movido automaticamente para a área de **Log de Auditoria** na interface, mantendo o histórico de quem tomou a decisão e a evidência fotográfica.
- 5. Caso a placa comparada nao tenha sido identificada como suspeita ira direto para o status **'limpo'** sem a necessidade de alguem aprovar.

## Passo 4 - Implementação Técnica (SQL)

&emsp; Conforme revisado no RF-03, o MVP não depende de GPS real — o drone Tello utilizado não possui módulo GPS. Por isso, o rastreamento operacional da Sprint 2 se apoia no `horario_scan` e no campo `localizacao` da tabela `operacoes` (zona de operação). Os campos `latitude` e `longitude` foram mantidos no schema apenas como **reserva de evolução futura** e não como parte obrigatória do fluxo validado nesta sprint. O schema das tabelas pode ser visto na Figura 1:

<div align="center">Figura 1: Imagem do Diagrama</div>
<div align="center"><img src="/img/sprint-2/Banco_de_Dados.png" alt="Diagrama do fluxo de interação do operador de drones com o sistema" /></div>
<div align="center">Fonte: Autores, 2026.</div>

O schema utilizado pelo projeto pode ser encontrado em `backend/schema/schema.sql`.
