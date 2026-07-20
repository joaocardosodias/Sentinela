---
sidebar_position: 3
title: Arquitetura da Informação
---

# Proposta da Primeira Arquitetura da Informação.

## Introdução

&emsp; A Arquitetura da Informação é a disciplina responsável por organizar, estruturar e hierarquizar conteúdos, funcionalidades e fluxos de interação dentro de um sistema. Seu objetivo é tornar a navegação mais intuitiva, eficiente e alinhada às necessidades dos usuários finais.

&emsp; Por meio dela, busca-se garantir que as informações certas estejam disponíveis no momento adequado, de forma clara, acessível e fácil de compreender. Assim, reduz-se a complexidade cognitiva do usuário e aumenta-se a eficiência na realização das tarefas dentro do sistema

&emsp; No contexto de projetos de sistemas interativos, a Arquitetura da Informação é fundamental para:
- Facilitar a localização de informações e o acesso a funcionalidades importantes;
- Apoiar a experiência do usuário, promovendo jornadas mais fluidas, simples e satisfatórias;
- Organizar os conteúdos de maneira lógica e coerente;
- Alinhar a estrutura do sistema às dores, necessidades, desejos e objetivos dos usuários.

&emsp; Dessa forma, uma Arquitetura da Informação bem definida não apenas melhora a usabilidade do sistema, como também contribui diretamente para sua eficácia, sua aceitação pelos usuários e o sucesso do projeto como um todo.

## Como Isso se Aplica no Projeto

### Visão Geral do Projeto

&emsp;O projeto consiste em uma plataforma de monitoramento e identificação de veículos roubados por meio do uso de drones. Os drones captam imagens das placas dos carros em determinada região e enviam essas imagens para um Backend local, onde é executado um modelo de inteligência artificial baseado em YOLO para reconhecer as placas dos veículos.

&emsp;Após a identificação da placa, o sistema compara as informações captadas com o banco de dados da Pier, verificando se o veículo consta como roubado ou não. Caso o veículo seja identificado como roubado, o sistema registra o frame do vídeo em uma DAM, ou seja, uma biblioteca de armazenamento de mídia, e informa o Gestor da Pier sobre a ocorrência.

&emsp; A aplicação foi criada para apoiar a Pier no processo de localização de veículos roubados de seus clientes, tornando a identificação mais automatizada, rápida e eficiente.

#### Problema que o sistema resolve

&emsp;Atualmente, um dos principais desafios após o roubo de um veículo é conseguir localizá-lo de forma rápida e confiável. O processo tradicional depende de buscas manuais, denúncias, sistemas externos ou ações policiais, o que pode tornar a recuperação do veículo mais lenta.

&emsp;A solução proposta busca reduzir essa dificuldade por meio da combinação de três elementos:

- Drones para captura de imagens em campo;
- Inteligência artificial para leitura e identificação de placas;
- Integração com o banco de dados da Pier para validação dos veículos roubados.

&emsp; Dessa forma, o sistema contribui para automatizar a busca por veículos roubados e oferecer uma visão organizada para os gestores responsáveis.


#### Objetivo da Arquitetura da Informação

&emsp; A Arquitetura da Informação desta aplicação tem como objetivo organizar as telas, informações, funcionalidades e fluxos de navegação de forma clara e eficiente, considerando os diferentes tipos de usuários do sistema.

&emsp; Como a plataforma possui perfis distintos de acesso, a estrutura da informação foi pensada para apresentar a cada usuário apenas os dados e funcionalidades relevantes para sua função.

&emsp; Dessa forma, busca-se:

- Facilitar o acesso às informações críticas;
- Reduzir a complexidade da navegação;
- Separar as funcionalidades de acordo com o perfil do usuário;
- Destacar alertas de veículos roubados;
- Permitir o acompanhamento dos drones em operação;
- Apoiar a tomada de decisão do Gestor da Pier.

#### Perfis de usuários

##### Operador de Drones

&emsp; O Operador de Drones é o usuário responsável pela operação direta dos drones em campo.

&emsp; Seu fluxo é bem simples, sem muito mistério:

<div align="center">Figura 1: Fluxo de Uso do Operador de Drones</div>
<div align="center"><img src="/img/sprint-1/drones.png" alt="Diagrama do fluxo de interação do operador de drones com o sistema" /></div>
<div align="center">Fonte: Autores, 2026.</div>

##### Gestor de Operações

&emsp; O Gestor de Operações é o usuário responsável pela gestão direta de todos os drones em campo.

&emsp; Seu fluxo é mais completo, já que ela irá interagir com o Front-End da aplicação:

<div align="center">Figura 2: Fluxo de Uso do Gestor de Operações</div>
<div align="center"><img src="/img/sprint-1/GestorDeDrones.png" alt="Diagrama do fluxo de interação do gestor de operações com o painel tático" /></div>
<div align="center">Fonte: Autores, 2026.</div>

&emsp; Essa área apresenta uma visão operacional dos drones utilizados no monitoramento.

&emsp; Conteúdos principais
- Câmera do drone;
- Identificação do drone;
- Status de conectividade;
- Nível de bateria;
- Mapa ou área de visualização da rota;
- Histórico de caminhos percorridos.

&emsp; Qual o Objetivo?

Permitir que o gestor acompanhe o desempenho dos drones, identifique problemas operacionais e consulte o histórico das rotas realizadas.

##### Gestor da Pier

&emsp; O Gestor da Pier é responsável por verificar quais placas vereficadas pelo nosso sistema são roubadas ou não.

&emsp; Seu fluxo necessita ser algo simples, mas completo:

<div align="center">Figura 3: Fluxo de Uso do Gestor da Pier</div>
<div align="center"><img src="/img/sprint-1/GestorDaPier.png" alt="Diagrama do fluxo de interação do gestor da Pier com as detecções" /></div>
<div align="center">Fonte: Autores, 2026.</div>

&emsp; Essa área apresenta os resultados das detecções feitas pelo sistema.

&emsp; Conteúdos principais
- Alertas de veículos roubados;
- Lista de veículos limpos;
- Placa identificada;
- Modelo do carro;
- Data e horário da detecção;
- Foto/frame do veículo;
- Status da ocorrência.

&emsp; Qual o Objetivo?

&emsp; Permitir que o Gestor da Pier acompanhe, de forma simples e rápida, quais veículos foram identificados como roubados e quais foram classificados como limpos.