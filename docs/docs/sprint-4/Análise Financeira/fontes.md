---
sidebar_position: 6
title: Fontes
---

# Fontes da Análise Financeira

&emsp;Esta seção reúne e organiza todas as fontes utilizadas como base para as premissas, estimativas e cálculos da análise financeira.



## Mercado Segurador

| Fonte | Uso na Análise | Link |
|---|---|---|
| **SUSEP** | Estatísticas do mercado segurador; índice de veículos roubados/furtados | [www2.susep.gov.br](https://www2.susep.gov.br/menuestatistica/rankroubo/menu1.asp) |
| **CNseg** | Estudos setoriais sobre sinistros e indenizações | — |
| **Youse** | Referência para cobertura 100% Tabela FIPE em roubo/furto | [youse.com.br](https://www.youse.com.br/seguro-auto/duvidas/coberturas/qual-o-valor-que-eu-recebo-de-indenizacao-com-a-cobertura-de-roubo/) |
| **Allianz** | Conteúdo de mercado sobre seguro contra roubo/furto | [allianz.com.br](https://www.allianz.com.br/Blog/2024/seguro-contra-roubo-e-furto.html) |
| **Neo Seguradora** | Indenização quando veículo roubado é recuperado | [neoseguradora.com.br](https://www.neoseguradora.com.br/post/como-fica-o-seguro-quando-o-carro-roubado-e-recuperado) |


## Recuperação de Veículos

| Fonte | Uso na Análise | Link |
|---|---|---|
| **SSP São Paulo / CNN Brasil** | Dado de +23 mil veículos recuperados no estado em 2024; referência de taxa de recuperação | [cnnbrasil.com.br](https://www.cnnbrasil.com.br/nacional/estado-de-sao-paulo-registra-menor-numero-de-roubos-da-historia-nos-primeiros-meses-de-2024/) |
| **Sinesp / Ministério da Justiça** | Base nacional de alerta e recuperação de veículos | — |



## Salários e Custo de Desenvolvimento

| Fonte | Uso na Análise | Link |
|---|---|---|
| **Glassdoor** | Salário de desenvolvedor Python sênior (~R$ 10,4 mil/mês); piloto de drone (~R$ 5,65 mil/mês) | [glassdoor.com.br](https://www.glassdoor.com.br/Sal%C3%A1rios/desenvolvedor-python-senior-sal%C3%A1rio-SRCH_KO0,27.htm) |
| **Robert Half** | Faixas para back-end sênior (R$ 12,4–R$ 20,9 mil/mês); front-end sênior (R$ 12,45–R$ 18,2 mil/mês) | [roberthalf.com](https://www.roberthalf.com/br/pt/vagas-detalhes/desenvolvedora-back-end-senior) |
| **Blog Anhanguera** | Referência de faixa para profissional de IA/visão computacional no Brasil | [blog.anhanguera.com](https://blog.anhanguera.com/quanto-ganha-um-profissional-de-ia-no-brasil/) |



## Regulamentação de Drones

| Fonte | Uso na Análise | Link |
|---|---|---|
| **ANAC** | Requisitos de habilitação para piloto remoto acima de 400 pés AGL; licença e autorização para RPA | [gov.br/anac](https://www.gov.br/anac/pt-br/assuntos/regulados/profissionais-da-aviacao-civil/habilitacao/licenca-e-autorizacao-especifica-para-piloto-de-rpa-drone) |
| **RBAC-E94** | Regulamento técnico de aeronaves não tripuladas | [anac.gov.br](https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-e-94) |



## Equipamentos

| Fonte | Uso na Análise | Link |
|---|---|---|
| **Extreme Concept (revendedor autorizado DJI)** | Preço de referência do DJI Mavic 3 Enterprise no Brasil (~R$ 33 mil) | [extremeconcept.com.br](https://www.extremeconcept.com.br/produtos/drone-dji-mavic-3-enterprise-anatel-br-com-3-bat-extras-valor-a-vista/) |



## Infraestrutura Cloud

| Fonte | Uso na Análise | Link |
|---|---|---|
| **Supabase Pricing** | Custos de banco e storage (plano Pro, US$ 25/mês base; US$ 0,021/GB) | [supabase.com/pricing](https://supabase.com/pricing) / [supabase.com/docs/guides/storage/pricing](https://supabase.com/docs/guides/storage/pricing) |



## Conectividade

| Fonte | Uso na Análise | Link |
|---|---|---|
| **Vivo Empresas** | Planos corporativos 4G: 40 GB = R$ 69,99; 100 GB = R$ 99,99 | [vivomovelempresa.com.br](https://www.vivomovelempresa.com.br/planos_4g) |



## Nota Metodológica

&emsp;Para estimativas de custo-hora de desenvolvimento, utilizou-se a seguinte lógica de conversão a partir de salários mensais:

$$\text{Custo-hora} = \frac{\text{Salário mensal}}{160 \text{ horas úteis/mês}}$$

&emsp;Exemplo: profissional de R$ 12.000/mês → ~R$ 75/hora (custo bruto, antes de encargos e overhead). Para contratação CLT, aplica-se multiplicador de ~1,7× sobre o salário bruto para refletir o custo real ao empregador.