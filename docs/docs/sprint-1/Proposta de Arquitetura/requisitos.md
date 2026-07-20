---
sidebar_position: 1
---

# Requisitos do Sistema
 
## Introdução
 
Este documento descreve os requisitos do sistema de fiscalização veicular autônoma por drone, desenvolvido para identificar placas de veículos com registro de roubo ou furto em tempo real. A solução combina captura de imagem aérea, visão computacional, geolocalização, monitoramento de conectividade dos drones e integração com a API da Pier para formar um pipeline completo de detecção e alerta. O objetivo central é reduzir o tempo entre a identificação de um veículo suspeito e a ação de resposta das equipes responsáveis, aumentando a probabilidade de recuperação do bem e fortalecendo a efetividade operacional em campo.
 
---
 
## Requisitos Funcionais
 
Os requisitos funcionais descrevem **o que o sistema deve fazer**, ou seja, as capacidades e comportamentos que ele precisa oferecer para cumprir seus objetivos.
 
### RF-01 - Captura de Imagem
 
O sistema deve ser capaz de capturar imagens nítidas de placas de veículos estacionados e em movimento através da câmera do drone.
 
### RF-02 - Visão Computacional
 
O sistema deve extrair os caracteres alfanuméricos das placas capturadas nas imagens recebidas do drone, utilizando visão computacional.
 
### RF-03 - Geolocalização
 
O sistema deve associar automaticamente as coordenadas de GPS (latitude e longitude) e o Date Time recebidos da telemetria do drone ao registro de cada placa identificada.
 
### RF-04 - Consulta de Sinistros
 
O sistema deve realizar uma chamada automática à API da Pier para verificar o status de roubo ou furto da placa capturada.
 
### RF-05 - Notificação de Match
 
Caso a placa conste na base de sinistros, o sistema deve gerar um alerta imediato contendo a placa, a localização exata e o Date Time de onde o veículo foi identificado.
 
### RF-06 - Health Check
 
O sistema deve garantir que os drones estão conectados e enviando dados da operação.
 
---
 
## Requisitos Não Funcionais
 
Os requisitos não funcionais definem **como o sistema deve se comportar**, abrangendo os atributos de qualidade, desempenho e restrições operacionais que garantem a efetividade da solução.
 
### RNF-01 - Tempo de Resposta
 
A consulta à base de dados e a geração do alerta devem ocorrer em até 5 segundos após a captura da imagem, evitando que a defasagem de localização comprometa a utilidade da informação em campo.
 
### RNF-02 - Velocidade de Match
 
O sistema deve realizar a verificação se a placa é roubada ou não em um tempo inferior a 5 segundos.
 
### RNF-03 - Latência de Alerta Crítico
 
Uma vez detectado um *match* positivo, o sistema deve disparar a notificação para o frontend e encaminhá-la à Pier em menos de 5 segundos, com o objetivo de aproveitar o pico de probabilidade de recuperação antes que o veículo seja removido do local.
 
### RNF-04 - Latência de Vídeo no Dashboard
 
O vídeo exibido no dashboard do gestor da operação deve apresentar uma latência inferior a 5 segundos, garantindo que as decisões operacionais sejam tomadas com base em imagens próximas ao tempo real.
 
### RNF-05 - Acurácia do Modelo
 
O modelo utilizado deve ser capaz de processar e registrar placas de veículos com pelo menos 80% de confiabilidade, assegurando a qualidade das leituras realizadas em campo.
 
### RNF-06 - Precisão de Georreferenciamento
 
A coordenada GPS registrada no momento do *match* deve ter um erro radial máximo de 5 metros, permitindo que a equipe de pronta resposta localize o veículo rapidamente em ruas densas ou galpões.
 
### RNF-07 - Health Check
 
A garantia de conectividade dos drones deve ser feita a partir das informações de telemetria enviadas pelo próprio drone, sem depender de mecanismos externos de verificação.
 
---
 
## Conclusão
 
Os requisitos funcionais e não funcionais descritos neste documento são interdependentes e se reforçam mutuamente para garantir a efetividade da solução. A **captura de imagem (RF-01)** é a base de todo o pipeline e tem sua qualidade assegurada pela **acurácia mínima de 80% do modelo (RNF-05)**, que garante que as leituras realizadas em voo sejam confiáveis. O módulo de **visão computacional (RF-02)** alimenta diretamente a **consulta de sinistros (RF-04)**, cuja agilidade é determinada pela **velocidade de match (RNF-02)**, que impõe um limite de 5 segundos para a verificação de cada placa.
 
A **geolocalização (RF-03)**, por sua vez, só entrega valor operacional real quando atendida a **precisão de georreferenciamento (RNF-06)**, que garante que as coordenadas registradas sejam precisas o suficiente para orientar equipes em campo. Já a **notificação de match (RF-05)** depende diretamente da **latência de alerta crítico (RNF-03)** e do **tempo de resposta geral (RNF-01)** para que a janela de oportunidade de recuperação do veículo seja aproveitada antes de sua locomoção. A **latência de vídeo no dashboard (RNF-04)** complementa esse ciclo ao garantir que o gestor da operação acompanhe os eventos em tempo próximo ao real, viabilizando decisões rápidas e coordenadas. Por fim, o **health check (RF-06)**, sustentado pelas informações de telemetria conforme definido em **RNF-07**, assegura a integridade operacional de toda a frota durante a missão, sendo condição essencial para que todos os demais requisitos possam ser cumpridos de forma contínua e confiável.