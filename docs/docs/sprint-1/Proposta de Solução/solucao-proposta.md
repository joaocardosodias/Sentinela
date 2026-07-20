---
sidebar_position: 1
---

# Proposta de Solução

&emsp;A partir da investigação realizada, torna-se evidente que o principal desafio da recuperação de veículos não está na identificação do problema, mas na **capacidade operacional de atuar sobre ele de forma eficiente**.

&emsp;Os achados indicam que a recuperação depende diretamente de três fatores críticos:

- Atuação em regiões de difícil acesso (dimensão espacial)  
- Resposta rápida dentro da janela crítica de recuperação (dimensão temporal)  
- Capacidade de busca contínua e escalável (dimensão operacional)  

&emsp;Nesse contexto, propõe-se o desenvolvimento de uma solução baseada em **robótica móvel e visão computacional**, capaz de ampliar a cobertura da operação, reduzir o tempo de resposta e automatizar o processo de identificação de veículos.

---

## Visão Geral da Solução

&emsp;A solução consiste em um sistema integrado de drones equipados com câmeras e algoritmos de visão computacional, responsáveis por realizar a **varredura aérea de regiões estratégicas**, identificar automaticamente placas de veículos e consultar, em tempo quase real, a base de sinistros da Pier.

&emsp;Diferentemente do modelo atual, baseado em busca manual, a solução permite uma operação:

- Independente de vias terrestres  
- Orientada por dados e priorização geográfica  
- Automatizada na identificação de veículos  
- Capaz de operar com maior escala e frequência  

&emsp;A proposta atua diretamente sobre os principais gargalos identificados na investigação, especialmente nas limitações de cobertura e tempo de resposta.

---

## Funcionamento da Solução

&emsp;O funcionamento do sistema pode ser descrito em quatro etapas principais:

### 1. Planejamento de Busca

&emsp;As áreas de varredura são definidas com base em padrões identificados na investigação, priorizando regiões com maior probabilidade de recuperação, como:

- Zonas de desova  
- Regiões periféricas com baixa acessibilidade  
- Áreas próximas a corredores de fuga  

&emsp;Esse direcionamento permite concentrar a operação em regiões com maior potencial de retorno.


### 2. Varredura Aérea

&emsp;Os drones realizam o sobrevoo das regiões definidas, capturando imagens de veículos estacionados ou em baixa movimentação.

&emsp;A utilização de varredura aérea permite:

- Superar barreiras geográficas (mata, terrenos irregulares, áreas isoladas)  
- Ampliar a cobertura em menor tempo  
- Reduzir a exposição de equipes humanas a ambientes de risco  


### 3. Identificação Automatizada de Placas

&emsp;As imagens capturadas são processadas por um sistema de visão computacional responsável por:

- Detectar veículos nas imagens  
- Identificar e extrair as placas  
- Realizar a leitura automática dos caracteres (ALPR)  

&emsp;O processamento ocorre localmente (edge computing), permitindo que a análise seja realizada em tempo quase real, reduzindo a dependência de conectividade e evitando atrasos causados pelo envio contínuo de dados para a nuvem.

&emsp;Além da leitura da placa, o sistema registra uma imagem do momento da detecção, contendo a marcação visual da placa, que será utilizada como evidência no processo.


### 4. Consulta e Geração de Alertas

&emsp;Cada placa identificada é automaticamente consultada na base de dados de sinistros da Pier.

&emsp;Em caso de correspondência positiva:

- A placa é validada como veículo com registro de roubo ou furto  
- A localização geográfica e o horário da detecção são registrados  
- A imagem capturada é associada ao evento como evidência  
- Um alerta é gerado para as equipes responsáveis  

&emsp;Esse processo ocorre de forma automatizada e em baixa latência, permitindo atuação dentro da janela crítica de recuperação.


---

## Alinhamento com a Investigação

&emsp;A solução proposta responde diretamente às dimensões identificadas na investigação:

### Dimensão Espacial

- Permite atuação em regiões de difícil acesso  
- Direciona a busca para zonas de desova  
- Amplia a cobertura geográfica da operação  

### Dimensão Temporal

- Reduz o tempo entre o roubo e a identificação do veículo  
- Permite atuação dentro da janela crítica de recuperação  
- Automatiza etapas que anteriormente eram manuais  

### Dimensão Operacional

- Aumenta a capacidade de busca sem dependência proporcional de mão de obra  
- Padroniza o processo de identificação e validação  
- Reduz a variabilidade da operação atual  
 

---

## Conclusão

&emsp;A solução proposta traduz os achados da investigação em uma abordagem tecnológica capaz de ampliar a eficiência da recuperação de veículos, ao combinar varredura aérea, automação e análise de dados.

&emsp;Ao atuar diretamente nas limitações espaciais, temporais e operacionais do modelo atual, o sistema estabelece uma base estruturada para evolução da operação de recuperação da Pier.