---
sidebar_position: 11
---

# Estimativa de Custos

&emsp;A estimativa de custos para implementação e operação da solução de identificação de veículos sinistrados por meio de drones e visão computacional foi estruturada em dois blocos principais: **investimento inicial (CAPEX)** e **custos operacionais recorrentes (OPEX)**.

&emsp;O objetivo é fornecer uma visão clara dos recursos necessários para viabilizar um piloto funcional do sistema, considerando as decisões arquiteturais adotadas, como o processamento em borda (edge computing), o uso de infraestrutura em nuvem para armazenamento seletivo de evidências e a operação assistida por um operador em campo.

&emsp;As estimativas foram baseadas em valores praticados no mercado brasileiro de tecnologia, utilizando como referência varejistas de hardware, pesquisas salariais e calculadoras oficiais de provedores de nuvem.

---

## Investimento Inicial (CAPEX)

&emsp;O investimento inicial contempla todos os custos necessários para a construção de um Produto Mínimo Viável (MVP), incluindo aquisição de hardware e desenvolvimento do sistema.

### Hardware

&emsp;O hardware é responsável por viabilizar a captura de imagens e o processamento local em tempo real. Considerando a arquitetura proposta, onde a visão computacional é executada em um computador local, é necessário um equipamento com GPU dedicada para suportar os modelos de detecção e reconhecimento de placas.

&emsp;Além disso, a qualidade da câmera do drone impacta diretamente a acurácia do sistema, sendo um fator crítico para a efetividade da solução.

Com base em preços praticados no mercado brasileiro:

- **Drone:**
    - Modelo de entrada: `R$ 800 a R$ 1.500`
    - Modelo com câmera 4K estabilizada: `R$ 6.000 a R$ 9.000`

- **Notebook com GPU dedicada:**
    - Faixa estimada: `R$ 6.000 a R$ 10.000`

- **Baterias e acessórios:**
    - Faixa estimada: `R$ 1.500 a R$ 2.500`

- **Equipamentos complementares (roteador ou modem portátil):**
    - Faixa estimada: `R$ 300 a R$ 600`

Dessa forma, o **investimento em hardware** pode variar entre: 
> `R$ 7.100 e R$ 22.100`

### Desenvolvimento

&emsp;O custo de desenvolvimento considera a construção de um MVP capaz de executar o fluxo completo da solução: captura de imagem, processamento por visão computacional, consulta à base de sinistros, armazenamento de evidências e visualização em interface web.

&emsp;As estimativas foram baseadas em valores médios de mercado para profissionais de tecnologia no Brasil (dados de plataformas como Glassdoor, GeekHunter e Workana), considerando contratação no modelo PJ ou freelancer.

- **Faixas de valor por hora:**

    - Backend: `R$ 80 a R$ 150 por hora`
    - Frontend: `R$ 70 a R$ 130 por hora`
    - Engenharia de IA / Visão Computacional: `R$ 120 a R$ 220 por hora`

- **Estimativa de esforço:**

    - Visão Computacional: 60 a 100 horas
    - Backend: 50 a 80 horas
    - Frontend: 40 a 60 horas

Total estimado: 150 a 240 horas

Com base nesses valores, o custo **total de desenvolvimento** situa-se entre:

> `R$ 15.000 e R$ 35.000`

### Síntese do CAPEX

O **investimento inicial total** para implementação da solução varia entre:

> `R$ 22.100 e R$ 57.100`

Essa variação está diretamente relacionada à escolha do hardware (principalmente o drone) e ao nível de especialização dos profissionais envolvidos no desenvolvimento.

---

## Custos Operacionais (OPEX)

&emsp;Os custos operacionais correspondem às despesas recorrentes necessárias para manter o sistema em funcionamento, incluindo infraestrutura digital, conectividade e operação em campo.

### Infraestrutura em Nuvem

&emsp;A arquitetura do sistema foi projetada para minimizar o consumo de recursos em nuvem, enviando apenas evidências relevantes (casos positivos). Isso reduz significativamente o custo operacional.

Com base nas calculadoras oficiais de provedores como AWS e Firebase:

- Armazenamento de imagens e evidências: `R$ 10 a R$ 30 por mês`
- Banco de dados: `R$ 0 a R$ 100 por mês`
- Servidor de API (instância de baixo porte): `R$ 50 a R$ 150 por mês`

O **custo total estimado de infraestrutura** é de:

> `R$ 60 a R$ 280 por mês`

### Conectividade

&emsp;A operação depende de conexão com a internet para consulta à API da Pier e envio das evidências à nuvem. Essa conectividade pode ser garantida por meio de planos móveis 4G ou 5G.

- Plano de dados móveis: `R$ 80 a R$ 150 por mês`

### Operação em Campo

&emsp;Os custos operacionais incluem a execução da operação com o drone, manutenção dos equipamentos e consumo energético.

- Operador de drone: `R$ 1.500 a R$ 3.000 por mês`
- Manutenção e reposição de peças: `R$ 100 a R$ 300 por mês`
- Energia elétrica: `R$ 20 a R$ 50 por mês`

O **custo total** dessa categoria é de:

> `R$ 1.620 a R$ 3.350 por mês`

### Síntese do OPEX

O **custo operacional** mensal total da solução é estimado entre:

> `R$ 1.760 e R$ 3.780 por mês`

---

## Considerações Finais

&emsp;A estrutura de custos apresentada demonstra que a solução possui um investimento inicial moderado e custos operacionais controlados, especialmente devido às decisões arquiteturais adotadas.

&emsp;O uso de processamento em borda reduz a dependência de infraestrutura em nuvem, enquanto o modelo de upload condicional evita o consumo desnecessário de banda e armazenamento.

Considerando os valores estimados:

- **Investimento inicial (CAPEX):** R$ 22.100 a R$ 57.100
- **Custo operacional mensal (OPEX):** R$ 1.760 a R$ 3.780

É possível projetar o custo total da solução ao longo do tempo. Em um horizonte de 12 meses de operação, o custo total estimado seria:

- **Cenário mínimo:** aproximadamente R$ 43.220
- **Cenário máximo:** aproximadamente R$ 102.460

&emsp;Observa-se que o principal custo recorrente está associado à operação humana, o que indica um potencial de redução futura com a evolução para níveis mais altos de automação.

&emsp;Dessa forma, a solução se mostra adequada para implementação em formato de piloto, permitindo validação técnica e operacional antes de uma possível expansão em escala.