---
sidebar_position: 3
---

# Estruturação do Problema

&emsp;A partir do entendimento do contexto operacional da Pier, torna-se evidente que o desafio da recuperação de veículos roubados ou furtados vai além de uma limitação pontual do processo atual. Trata-se de um problema estrutural, que envolve restrições operacionais, limitações tecnológicas e impacto direto no modelo de negócio da seguradora.

### Impacto no negócio

&emsp;A não recuperação de veículos sinistrados representa um **alto custo** para a Pier. Quando um veículo não é localizado, a seguradora precisa realizar a indenização ao cliente, o que gera prejuízo direto e impacta negativamente a sinistralidade da carteira.

&emsp;Atualmente, a Pier registra aproximadamente 70 casos de roubo ou furto por mês, dos quais apenas cerca de 5 a 7 são recuperados, evidenciando uma **taxa de recuperação significativamente baixa**. Esse cenário reforça a necessidade de aumentar a eficiência da recuperação como forma de reduzir custos e melhorar o desempenho financeiro da operação.

### Limitações operacionais

&emsp;O processo atual de recuperação é baseado no modelo de "pronta resposta", no qual uma empresa terceirizada realiza buscas ativas em campo. Nessa operação, agentes percorrem regiões urbanas observando veículos estacionados e, ao identificar um possível alvo, realizam consultas manuais de placa em sistemas externos para verificar a existência de sinistros.

Para melhor compreensão do processo atual, a operação de pronta resposta pode ser descrita nas seguintes etapas:

1. **Agente em campo:** Agentes percorrem regiões de risco observando veículos estacionados  

2. **Pesquisa de placa:** Ao identificar um veículo suspeito, consultam a placa em sistemas externos  

3. **Identificação:** O sistema verifica se o veículo é segurado e possui registro de roubo/furto  

4. **Acionamento:** Em caso de correspondência, a polícia e a seguradora são acionadas  

5. **Resguardo do bem:** A equipe acompanha o veículo até a chegada da polícia

A partir desse fluxo, é possível identificar limitações estruturais relevantes:

- Cobertura geográfica restrita, dependente da quantidade de agentes disponíveis  
- Operação limitada a horários específicos, sem atuação contínua  
- Alto custo operacional associado à terceirização  
- Processo manual e pouco escalável  

&emsp;Além disso, a comunicação entre a equipe de campo e a Pier ocorre majoritariamente por canais informais, como WhatsApp, o que evidencia baixa padronização e pouca integração tecnológica no fluxo.

&emsp;Outro ponto relevante é a dependência de incentivos individuais para o funcionamento da operação. As equipes terceirizadas recebem recompensas financeiras pela identificação de veículos, o que introduz variabilidade na execução e torna a performance dependente da iniciativa dos agentes. Como consequência, a cobertura e a eficiência da busca tornam-se difíceis de prever e padronizar.

&emsp;O fluxo de validação também apresenta etapas manuais e sequenciais. Após a identificação de um veículo suspeito, a equipe entra em contato com a Pier, que realiza a verificação da placa e confirma a existência de sinistro. Somente após essa validação ocorre o acionamento das autoridades, o que adiciona latência ao processo em um contexto altamente sensível ao tempo. Em cenários de maior risco, as equipes podem optar por não permanecer no local, limitando-se ao registro visual e comunicação remota. Esse comportamento, embora necessário do ponto de vista de segurança, pode comprometer a efetividade da recuperação.


### Janela crítica de recuperação

&emsp;Um fator crítico identificado no processo é o tempo. Após o roubo, é comum que o veículo passe por um **período de “esfriamento”**, no qual permanece estacionado por algumas horas ou dias enquanto os criminosos verificam a presença de rastreadores ou risco de recuperação.

&emsp;Esse intervalo representa a principal **oportunidade de recuperação do veículo**. No entanto, a partir dos relatos operacionais, observa-se um indício de que a probabilidade de recuperação tende a diminuir com o passar do tempo, especialmente após os primeiros dias do sinistro. Essa hipótese será investigada nas etapas seguintes do projeto.

&emsp;Na prática, isso significa que atrasos na identificação e localização do veículo reduzem drasticamente as chances de recuperação, tornando o tempo um fator determinante para o sucesso da operação.


### Distribuição espacial do problema

&emsp;Outro aspecto relevante é a dinâmica espacial dos roubos. De acordo com o relato do parceiro, há indícios de que os locais de roubo e os locais onde os veículos são posteriormente encontrados tendem a ser diferentes.

&emsp;Frequentemente, os veículos são deslocados para regiões mais isoladas, próximas a desmanches ou áreas de difícil acesso, onde permanecem durante o período de “esfriamento”. Essas regiões, muitas vezes chamadas informalmente de **zonas de desova**, apresentam características específicas:

- Baixa circulação de pessoas  
- Maior dificuldade de acesso  
- Menor presença de fiscalização  

&emsp;Apesar desses indícios, a Pier ainda não possui uma base de dados estruturada que permita validar e mapear esses padrões com precisão. Dessa forma, a existência e a relevância dessas zonas serão investigadas nas próximas etapas do projeto.


## Síntese do problema

&emsp;A partir da análise realizada, o problema pode ser sintetizado como a dificuldade de realizar uma busca eficiente, escalável e em tempo hábil para localizar veículos roubados durante a janela crítica de recuperação.

Essa limitação é resultado da combinação de:

- Baixa cobertura geográfica da operação atual
- Dependência de processos manuais
- Restrição temporal crítica
- Falta de dados estruturados sobre padrões espaciais

&emsp;Diante desse cenário, torna-se necessário investigar de forma estruturada os fatores que influenciam a recuperação de veículos, com foco especial nas **dimensões temporal e espacial** identificadas. Essa investigação orientará a definição de soluções capazes de ampliar a capacidade de busca, reduzir o tempo de resposta e **aumentar a eficiência da operação**.

---

## Referências

PIER SEGURADORA. Apresentação institucional e descrição do processo de recuperação de veículos. Material fornecido durante reunião de kickoff do projeto, 2026. Documento não publicado.