---
sidebar_position: 5
---

# Investigação: 1ª Hipótese

A primeira hipótese do projeto propõe que:

> Existem clusters geográficos com maior incidência de roubo e furto de veículos, e esses locais são diferentes das regiões de desmanche ou abandono ("zonas de desova"). Além disso, essas regiões tendem a possuir baixa acessibilidade, o que limita operações humanas de busca.

&emsp;A tese central que deriva desta hipótese postula que a recuperação de veículos esbarra na limitação da capacidade humana de cobertura geográfica. Como os criminosos tendem a abandonar os veículos temporariamente em locais conhecidos ("zonas de esfriamento") para verificar a presença de rastreadores, uma varredura aérea focada exclusivamente nessas zonas é operacionalmente mais ágil e possui uma taxa de conversão significativamente maior do que o patrulhamento humano tradicional.

&emsp;No mercado segurador, a validação dessa dinâmica espacial é crucial. Para a Pier Seguradora, a localização do veículo subtraído dita a saúde financeira da carteira. De acordo com as diretrizes do setor de seguros, se o carro for localizado *antes* do pagamento da indenização (que ocorre num prazo de até 30 dias após a entrega dos documentos), o repasse do valor integral é suspenso. Caso seja localizado após o pagamento, a posse é transferida para a seguradora, que pode comercializar o salvado ou suas peças em leilão, mitigando a perda [[4](#ref-neo)]. Portanto, direcionar esforços para os clusters geográficos corretos de forma ágil altera diretamente a sinistralidade.

---

# Validação da Hipótese

A validação da hipótese exigiu a análise da dinâmica espacial do crime, dividida em quatro dimensões estruturais:

1. **A geografia da subtração (Onde ocorre o roubo?)**
2. **A desconexão vetorial (A separação entre roubo e destino)**
3. **O atrito topográfico do esfriamento (Onde o ativo é ocultado?)**

---

## 1. A Geografia da Subtração

&emsp;Os dados mais recentes de segurança pública demonstram que os crimes contra veículos não ocorrem de forma pulverizada ou homogênea, mas concentram-se em clusters específicos que facilitam a operação criminal. 

&emsp;Segundo levantamento do [InfoMoney](#ref-infomoney) com base em dados da Secretaria de Segurança Pública (SSP-SP), o estado de São Paulo registrou em 2025 registrou uma média de 138 furtos ou roubos de veículos por dia. Somente entre janeiro e agosto, foram subtraídos 22.228 carros e 11.201 motos. Contudo, essa mancha criminal não é aleatória.

### 1.1. Distribuição Geográfica dos Roubos

&emsp;De acordo com análises do Núcleo de Estudos da Violência da USP (NEV-USP), a incidência de subtrações está intimamente conectada às rotas de fuga. O criminoso prioriza locais que garantam acesso imediato a vias expressas, rodovias e divisas municipais [[1](#ref-infomoney)].

&emsp;Neste cenário, a Zona Leste (ZL) e a Zona Sul (ZS) destacam-se como os maiores vetores de risco, impulsionadas tanto pela densidade demográfica quanto pela infraestrutura viária. Levantamentos da [Mobiauto](#ref-mobiauto) do primeiro semestre de 2025 corroboram a discrepância por região:

| Região | Bairros Críticos (Ocorrências - 1º Sem/2025) | Perfil Analítico da Área |
|--------|----------------------------------------------|--------------------------|
| **Zona Leste** | São Matheus (616); Tatuapé (615); Vila Matilde (501); Pq. São Lucas (430) | Maior pólo de risco absoluto. Combina alta movimentação comercial (Tatuapé) e acesso capilarizado a rodovias. |
| **Zona Sul** | Campo Limpo (439); Ipiranga (406); Santo Amaro (401); Capão Redondo (361) | Segunda maior densidade de ocorrências; bairros de conexão entre centros financeiros e as áreas periféricas. |
| **Zona Oeste** | Perdizes (434); Lapa (404); Pinheiros (267); CEAGESP (255) | Concentração de veículos com maior valor de mercado, alvos de quadrilhas especializadas. |
| **Zona Norte** | Pirituba (295); Casa Verde (291); Carandiru (283) | Vias de escoamento para municípios vizinhos e rota de veículos pesados. |
| **Centro** | Cambuci (369); Aclimação (199); Brás (173) | Área com altíssima circulação diurna; foco predominantemente voltado para furtos rápidos e furtos de motocicletas. |

&emsp;Enquanto bairros centrais e o Tatuapé figuram como alvos pela intensa movimentação e vulnerabilidade (especialmente para motocicletas no centro), as rotas de escoamento rápido fazem da Zona Leste a principal mancha de calor no momento do delito [[10](#ref-seguroauto)].

<div align="center">    
    <sup>Figura 1: Mapa de áreas com maior risco de roubo e furto em São Paulo</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1777593422/Foto-83_bhim3t.webp" style={{width: '100%'}} alt="Tela de Login e Cadastro" />
    <sup>Fonte: CNN Brasil, 2025. Acesso em: https://www.cnnbrasil.com.br/nacional/sudeste/sp/mapa-mostra-areas-com-maior-risco-de-roubo-e-furto-de-veiculos-em-sao-paulo/</sup>
</div>

&emsp;Além da concentração por bairros, os dados do [Mapa do Crime do Jornal O Globo](#ref-mapa-globo) evidenciam um padrão ainda mais específico: a recorrência de roubos em vias estruturais da cidade.

&emsp;Entre os locais com maior incidência de roubo de veículos, destacam-se:

- Estrada do M'Boi Mirim (44 ocorrências)
- Avenida Sapopemba (29)
- Rodovia Ayrton Senna (27)
- Estrada de Itapecerica (27)
- Avenida Raimundo Pereira de Magalhães (25)
- Estrada do Alvarenga (23)

&emsp;No caso de motocicletas, o padrão se repete, com forte presença de rodovias e avenidas de conexão:

- Estrada do M'Boi Mirim (47)
- Estrada do Alvarenga (46)
- Rodovia Anhanguera (46)
- Rodovia Raposo Tavares (30)
- Avenida Jacu-Pêssego (26)

&emsp;Dessa forma, os dados indicam que o local do roubo não é apenas um ponto de oportunidade, mas parte de uma lógica operacional estruturada, na qual os crimes se concentram em **corredores de mobilidade urbana**. Esses eixos priorizam mobilidade, conectividade e fuga, permitindo a rápida dispersão do veículo e seu deslocamento das áreas centrais para regiões periféricas, onde se localizam as zonas de ocultação.

### 1.2. Mapeamento Interativo da Concentração

&emsp;Para materializar essa densidade, o cruzamento de microdados de mais de 330 mil Boletins de Ocorrência alimentou a ferramenta [Mapa do Crime de São Paulo](https://infograficos.oglobo.globo.com/brasil/mapa-do-crime-sp.html), produzida pelo Jornal O Globo. A ferramenta, que corrige inconsistências de data da SSP via IA, demonstra visualmente a saturação de ocorrências nos eixos Leste e Sul da capital paulista.

---

## 2. A Desconexão Vetorial: Roubo vs. Desova

&emsp;Do ponto de vista operacional da seguradora, o dado mais crítico não é onde o carro foi levado, mas **para onde ele é direcionado nas horas subsequentes**. As evidências apontam para uma separação cirúrgica entre o local do crime (focado na oportunidade) e a zona de desova (focada na ocultação).

### 2.1. O Fenômeno do "Saldo Positivo" nos Extremos

&emsp;A prova quantitativa de que o crime funciona em "vetores de deslocamento" reside no saldo de recuperações dos Distritos Policiais (DPs). Análises históricas e projetadas evidenciam que uma pequena minoria de delegacias localizadas nas franjas da cidade recuperam mais veículos do que os que são roubados em sua própria jurisdição.

&emsp;A região da Vila Penteado (ZN), por exemplo, já chegou a figurar com saldo positivo de 379 veículos achados a mais do que os roubados localmente, fenômeno que se repete no Sacomã (ZS), Jardim Taboão (ZS), Jardim Miriam (ZS), Cidade Tiradentes (ZL) e Capão Redondo (ZS) [[9](#ref-r7)]. O diagnóstico é evidente: as extremidades da metrópole atuam como pontos receptores (desova) para os crimes cometidos nas áreas comerciais.

### 2.2. A Tática de Ocultação e "Esfriamento"

&emsp;Diferentemente dos furtos de oportunidade, o roubo (mediante grave ameaça) desencadeia um acionamento quase instantâneo do sistema policial [[6](#ref-oglobo26)]. Cientes do risco, os criminosos não enviam o veículo diretamente ao galpão de desmanche.

&emsp;Eles operam a tática de "esfriamento": o ativo é estacionado em uma zona intermediária e abandonado temporalmente, testando a presença de rastreadores veiculares ou bloqueadores remotos. Casos documentados pela [Polícia Civil de Goiás (PC-GO)](#ref-pcgo) e pela [Polícia Rodoviária Federal da Paraíba (PRF)](#ref-prf) corroboram essa tática. Em 2026, por exemplo, um SUV (Tiggo 7) roubado foi localizado poucas horas depois abandonado de forma premeditada em um "matagal denso" em Campina Grande (PB), ratificando o modus operandi que se repete nos pólos urbanos.

---
## 3. O Atrito Topográfico das Zonas de Desova

&emsp;A validação final da tese se dá pela correlação entre a ineficiência humana e a topografia dos clusters de desova. Por que, mesmo com a inteligência apontando as zonas periféricas, a recuperação terrestre é ineficiente?

&emsp;Segundo a inteligência de dados consolidados pelo Mapa do Crime do Jornal [O Globo](#ref-oglobo26) em 2026, **um em cada quatro roubos** de automóveis paulistanos converge para apenas cinco distritos no "fundão" urbano: São Mateus, São Rafael, Cidade Tiradentes (ZL), Jardim Herculano e Campo Limpo (ZS). Enquanto o índice geral de roubos na cidade declinava, esses distritos registraram 969 ocorrências, num aumento isolado de 13%.

### 3.1. Barreiras Geográficas à Operação Terrestre

Esses distritos foram escolhidos pela criminalidade por compartilharem os seguintes limitadores de acessibilidade [[5](#ref-especial-globo)]:

1. **Topografia de Cobertura (Descampados e Terrenos Baldios):** Áreas extensas com mato alto impossibilitam a visualização do veículo ao nível da rua. Os criminosos utilizam essa camuflagem para esconder temporariamente o carro ou, em último caso, realizar incêndios criminosos sem chamar atenção imediata.
2. **Isolamento Hídrico e Florestal:** Os distritos da Zona Sul (como Jardim Herculano) são colados em áreas de proteção e às margens das Represas Billings e Guarapiranga. Trata-se de terrenos acidentados, sem asfaltamento e de locomoção extremamente restrita para viaturas normais [[6](#ref-oglobo26)].
3. **Proximidade Logística:** O esfriamento em matagais nessas regiões ocorre a poucos quilômetros de galpões de desmanche clandestinos, não registrados pelo Detran-SP, reduzindo a distância de translado das peças após a desmontagem final.

<div align="center">    
    <sup>Figura 2: Mapa de concentração de roubo de veículos</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1777599147/dia-3-grafico-1-branco_qjn4vm.avif" />
    <sup>Fonte: Jornal O Globo, 2026. Acesso em: https://oglobo.globo.com/brasil/noticia/2026/04/28/roubos-de-veiculos-em-sao-paulo-funcionam-de-maneira-diferente-nas-zonas-leste-e-sul-entenda-por-que.ghtml</sup>
</div>


### 3.2. A Assimetria da Busca

&emsp;Essas características impõem um atrito severo à recuperação terrestre. Na operação da PRF de 2026, por exemplo, foi necessário o auxílio de um guincho especial para remover o automóvel do local de difícil acesso [[8](#ref-prf)]. Viaturas policiais convencionais não conseguem patrulhar rotineiramente o interior de matagais ou as margens isoladas de represas.


---

# Conclusão

&emsp;A análise estruturada dos dados de 2025 e 2026 consolida a validade da hipótese: os clusters de subtração (zonas comerciais e vias de alta circulação) são distintos dos clusters de desova (extremos Sul e Leste, marcados por áreas de mata, represas e baixa urbanização), e as barreiras geográficas destes últimos inviabilizam buscas terrestres eficientes.

&emsp;Mais do que uma diferença espacial, observa-se um fluxo operacional estruturado: o crime ocorre em áreas de alta mobilidade e o veículo é rapidamente deslocado para regiões de baixa visibilidade e difícil acesso. Essa dinâmica cria uma assimetria crítica, na qual a geografia favorece a ocultação e limita a capacidade de resposta das operações tradicionais.

&emsp;Para o mercado segurador, isso implica que o principal gargalo na recuperação não é a identificação do padrão, mas a capacidade de atuação sobre ele. O patrulhamento terrestre, restrito por vias e visibilidade, torna-se insuficiente diante de áreas extensas e pouco acessíveis.

&emsp;Nesse contexto, tecnologias de varredura aérea surgem como solução diretamente alinhada ao problema identificado. Ao operar de forma independente das barreiras topográficas, drones permitem a inspeção rápida e direcionada dessas regiões críticas, aumentando significativamente a probabilidade de recuperação dentro do período de "esfriamento" e reduzindo a exposição da seguradora a indenizações integrais.

---

## Referências


1. <span id="ref-infomoney"></span> **INFOMONEY (2025).** São Paulo tem 138 roubos e furtos de veículos por dia; veja os modelos mais visados. Disponível em: [https://www.infomoney.com.br/brasil/sao-paulo-tem-138-roubos-e-furtos-de-veiculos-por-dia-veja-os-modelos-mais-visados/](https://www.infomoney.com.br/brasil/sao-paulo-tem-138-roubos-e-furtos-de-veiculos-por-dia-veja-os-modelos-mais-visados/). Acesso em: 29 abr. 2026.

2. <span id="ref-mapa-globo"></span> **MAPA DO CRIME DE SÃO PAULO - O GLOBO (2023-2026).** Ferramenta interativa de cruzamento de microdados da Secretaria de Segurança Pública de São Paulo. Disponível em: [https://infograficos.oglobo.globo.com/brasil/mapa-do-crime-sp.html](https://infograficos.oglobo.globo.com/brasil/mapa-do-crime-sp.html). Acesso em: 29 abr. 2026.

3.  <span id="ref-mobiauto"></span> **MOBIAUTO (2025).** Qual bairro tem o maior número de roubos de carros em São Paulo? Disponível em: [https://www.mobiauto.com.br/revista/qual-bairro-tem-o-maior-numero-de-roubos-de-carros-em-sao-paulo/8856](https://www.mobiauto.com.br/revista/qual-bairro-tem-o-maior-numero-de-roubos-de-carros-em-sao-paulo/8856). Acesso em: 29 abr. 2026.

4. <span id="ref-neo"></span> **NEO SEGURADORA.** Como fica o seguro quando o carro roubado é recuperado. Disponível em: [https://www.neoseguradora.com.br/post/como-fica-o-seguro-quando-o-carro-roubado-e-recuperado](https://www.neoseguradora.com.br/post/como-fica-o-seguro-quando-o-carro-roubado-e-recuperado). Acesso em: 29 abr. 2026.

5. <span id="ref-especial-globo"></span> **O GLOBO (2026).** Roubo de carro avança em bairros da periferia de São Paulo próximos a áreas de mata, descampados e represas. Disponível em: [https://oglobo.globo.com/brasil/especial/roubo-de-carro-avanca-em-bairros-da-periferia-de-sao-paulo-proximos-a-areas-de-mata-descampados-e-represas.ghtml](https://oglobo.globo.com/brasil/especial/roubo-de-carro-avanca-em-bairros-da-periferia-de-sao-paulo-proximos-a-areas-de-mata-descampados-e-represas.ghtml).

6. <span id="ref-oglobo26"></span> **O GLOBO (2026).** Roubos de veículos em São Paulo funcionam de maneira diferente nas zonas Leste e Sul; entenda por quê. Disponível em: [https://oglobo.globo.com/brasil/noticia/2026/04/28/roubos-de-veiculos-em-sao-paulo-funcionam-de-maneira-diferente-nas-zonas-leste-e-sul-entenda-por-que.ghtml](https://oglobo.globo.com/brasil/noticia/2026/04/28/roubos-de-veiculos-em-sao-paulo-funcionam-de-maneira-diferente-nas-zonas-leste-e-sul-entenda-por-que.ghtml). Acesso em: 29 abr. 2026.

7. <span id="ref-pcgo"></span> **POLÍCIA CIVIL GO (2018).** Policiais civis monitoram áreas de “esfriamento” e recuperam veículo roubado. Disponível em: [https://goias.gov.br/policiacivil/policiais-civis-monitoram-areas-de-esfriamento-e-recuperam-veiculo-roubado/](https://goias.gov.br/policiacivil/policiais-civis-monitoram-areas-de-esfriamento-e-recuperam-veiculo-roubado/). Acesso em: 29 abr. 2026.

8. <span id="ref-prf"></span> **POLÍCIA RODOVIÁRIA FEDERAL - PB (2026).** PRF localiza veículo roubado escondido em matagal em Campina Grande. Disponível em: [https://www.gov.br/prf/pt-br/noticias/estaduais/paraiba/2026/abril/prf-localiza-veiculo-roubado-escondido-em-matagal-em-campina-grande](https://www.gov.br/prf/pt-br/noticias/estaduais/paraiba/2026/abril/prf-localiza-veiculo-roubado-escondido-em-matagal-em-campina-grande). Acesso em: 29 abr. 2026.

9. <span id="ref-r7"></span> **R7 (2014/2025).** Sete bairros concentram desova de carros roubados na capital paulista. Disponível em: [https://noticias.r7.com/sao-paulo/sete-bairros-concentram-desova-de-carros-roubados-na-capital-paulista-03022014/](https://noticias.r7.com/sao-paulo/sete-bairros-concentram-desova-de-carros-roubados-na-capital-paulista-03022014/). Acesso em: 29 abr. 2026.

10. <span id="ref-seguroauto"></span> **SEGURO AUTO (2024).** Carros mais roubados do Brasil. Disponível em: [https://www.seguroauto.org/carros-mais-roubados-do-brasil/](https://www.seguroauto.org/carros-mais-roubados-do-brasil/). Acesso em: 29 abr. 2026.