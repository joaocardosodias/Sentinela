---
sidebar_position: 1
title: Arquitetura do Sistema V2
---

# Arquitetura do Sistema V2

## Diagrama de Arquitetura

A arquitetura V2 itera a proposta da Sprint 1 ao explicitar as tecnologias utilizadas, os protocolos de comunicação e a separação entre operação local, serviços remotos e integrações externas.

<div align="center">Figura 1: Diagrama da Arquitetura V2 da Solução</div>
<div align="center"><img src="/img/sprint-2/arquitetura/arquitetura_sistema_M06.png" alt="Diagrama da arquitetura V2 do sistema, com frontend local, backend local, drone DJI Tello, API Pier, Supabase, backend remoto e frontend remoto" /></div>
<div align="center">Fonte: Autores, 2026.</div>

Arquivo editável: [arquitetura_sistema_M06.drawio](/img/sprint-2/arquitetura/arquitetura_sistema_M06.drawio).

---

## Visão Geral

A solução mantém uma arquitetura distribuída entre a operação em campo e a camada remota. A camada local concentra o controle da missão, o recebimento do vídeo do drone e o processamento de visão computacional. A camada remota sustenta a consulta, auditoria e visualização posterior das identificações realizadas.

Nesta Sprint 2, porém, esse diagrama deve ser lido como **arquitetura-alvo de curto prazo**, não como retrato de integração total já concluída no repositório. A implementação efetivamente entregue prioriza backend, persistência, CLI e provas técnicas de conexão com drone e visão computacional.

As principais tecnologias definidas para esta versão são React nos frontends, Python com Flask nos backends, YOLOv8 para visão computacional, PostgreSQL via Supabase para persistência e API REST para integração com a Pier.

---

## Justificativa das tecnologias e protocolos

A escolha de cada peça da stack privilegiou custo de aprendizado da equipe, integração com visão computacional e machine learning e adequação ao cenário de operação (local com baixa latência e nuvem para persistência e acompanhamento remoto), em detrimento de alternativas que exigiriam mais tempo de capacitação ou maior complexidade operacional neste estágio do projeto.

### 1. Python

Python foi adotado pela facilidade de integração com pipelines de visão computacional e pelo ecossistema consolidado em machine learning e VC (bibliotecas, exemplos e comunidade). Em comparação com linguagens de menor nível ou com curvas de integração ML menos maduras, Python reduz o risco técnico e acelera experimentação e manutenção do motor de detecção.

### 2. Flask

Flask foi escolhido como microframework para expor a API, pois toda a equipe já possui experiência prévia com ele em outros projetos, o que aumenta a previsibilidade do desenvolvimento, revisão de código e onboarding. Frente a frameworks full-stack mais opinativos ou a stacks assíncronas mais exigentes em configuração, Flask oferece superfície pequena e controle explícito sobre rotas e middlewares, alinhado ao escopo atual dos backends local e remoto.

### 3. Supabase (PostgreSQL como serviço)

Supabase foi utilizado como camada de Backend as a Service (BaaS) sobre PostgreSQL, pois o grupo já conhece o modelo de uso (API HTTP, autenticação e recursos típicos de BaaS), reduzindo o esforço de infraestrutura frente a um banco gerenciado “cru” com montagem manual de toda a camada de acesso, ou a um ORM e deploy de banco totalmente customizados desde o início.

### 4. React (frontends)

React foi definido para os frontends pela versatilidade do ecossistema e pela grande oferta de componentes e padrões de interface (incluindo modais e bibliotecas de UI), o que encurta o ciclo de construção de telas operacionais. Em relação a outros frameworks de interface, a decisão favoreceu a familiaridade do mercado e a reutilização de soluções prontas para padrões comuns de dashboard e formulários.

### 5. YOLOv8 (visão computacional)

YOLOv8 foi escolhido em primeiro lugar por combinar modelo relativamente leve, desempenho relevante em detecção e boa capacidade de fine-tuning, permitindo adaptar o reconhecimento ao domínio de placas e ao hardware disponível. Há margem de evolução: é possível migrar no futuro para arquiteturas mais recentes ou mais específicas ao problema. A linha evolutiva desejada inclui ainda a construção de um modelo proprietário do grupo, a partir de fine-tuning com YOLOv8 nano como base, equilibrando custo computacional em borda e qualidade da detecção.

### 6. REST, HTTP e UDP na comunicação

A API REST sobre HTTP foi mantida para integração com a Pier e para comunicação cliente–servidor nos frontends, por ser amplamente interoperável e simples de depurar. O UDP permanece associado ao vídeo do drone e a fluxos que exigem baixa latência, aceitando perdas pontuais de pacotes em troca de fluidez — cenário em que HTTP em streaming seria menos adequado para a mesma restrição de tempo na operação em campo.

---

## Componentes da Arquitetura

### 1. Frontend Local

Interface em React planejada para a operação em campo. Na Sprint 2, ela permanece como direção arquitetural documentada, sem equivaler a uma entrega operacional consolidada no repositório.

### 2. Backend Local

Serviço em Python com Flask responsável por orquestrar a operação local. Na implementação disponível nesta sprint, o backend já entrega autenticação via JWT, CRUDs principais e persistência. A integração contínua com vídeo, telemetria e visão computacional ainda está em estágio incremental.

Também é responsável por persistir dados no Supabase por meio da API HTTP e por comunicar eventos relevantes ao Frontend Local.

### 3. Drone DJI Tello

Drone utilizado para captura do vídeo da operação. A comunicação com o Backend Local ocorre por UDP, priorizando baixa latência no envio do vídeo para processamento.

### 4. PIER REST API

Serviço externo consultado pelo Backend Local via API REST para verificar se a placa identificada possui correspondência com registros de interesse.

### 5. Banco de Dados

Camada de persistência baseada em PostgreSQL e disponibilizada via Supabase. Centraliza os dados de operação, matches e registros necessários para auditoria, sendo acessada pelos backends local e remoto por HTTP / Supabase API.

### 6. Backend Remoto

Serviço em Python com Flask previsto para manter o Frontend Remoto em operação quando não há missão local em andamento e executar rotinas de auditoria assíncrona. Na Sprint 2, essa camada está descrita como evolução arquitetural, não como componente plenamente implementado no repositório.

### 7. Frontend Remoto

Interface em React voltada ao acompanhamento remoto. Na Sprint 2, ela permanece como componente planejado da arquitetura evolutiva.

---

## Fluxo de Comunicação

1. No fluxo-alvo, o Drone DJI Tello envia o vídeo ao Backend Local por UDP.
2. No fluxo-alvo, o Backend Local processa o vídeo com YOLOv8, extrai informações de placas e consulta a PIER REST API.
3. Na entrega atual, o núcleo validado é o registro e consulta de dados operacionais via backend + banco + CLI.
4. Os dados relevantes da operação são registrados no Supabase/PostgreSQL.
5. As camadas remotas de auditoria e visualização permanecem como evolução documentada.

---

## Considerações

A V2 reforça a decisão de processar vídeo e visão computacional localmente para reduzir latência durante a missão. A camada remota fica focada em continuidade da interface, consulta histórica, auditoria e visualização dos resultados, evitando dependência direta da conectividade externa para a operação crítica em campo.
