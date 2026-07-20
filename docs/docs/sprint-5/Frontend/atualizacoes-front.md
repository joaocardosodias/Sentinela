---
sidebar_position: 1
---

# Atualizações da Interface do Gestor Remoto


Nesta sprint foram realizadas melhorias na interface do Gestor Remoto com o objetivo de tornar o processo de validação de veículos mais eficiente e fornecer maior suporte à tomada de decisão. As alterações concentraram-se em dois pontos principais: a possibilidade de edição das informações identificadas automaticamente pelo sistema durante a validação de matches pendentes e a criação de uma nova aba de análises com indicadores operacionais.

Essas melhorias aumentam a confiabilidade dos dados registrados pelo sistema, reduzem a necessidade de correções posteriores e oferecem uma visão mais completa do funcionamento da operação.

---

## Campos Editáveis em Matches Pendentes


Durante o processo de validação de um match positivo, o gestor remoto analisa as informações coletadas pelo drone antes de aprovar ou rejeitar o alerta. Entretanto, na versão anterior da interface, todos os dados do veículo eram apresentados apenas para consulta, impossibilitando qualquer correção quando eram identificadas inconsistências provenientes do reconhecimento automático.

Embora o modelos de visão computacional apresentem alta precisão, fatores como iluminação, ângulo da câmera, distância do veículo ou obstruções parciais podem ocasionar erros na identificação da placa. Além disso, o modelo não reconhece a cor ou o modelo do veículo, sendo dados mockados que aparecem na interface. Dessa forma, permitir a intervenção do gestor torna o processo de validação mais confiável.

### Interface Atualizada

A modal de validação foi reformulada para permitir a edição dos campos de placa, cor e modelo do veículo antes da confirmação da análise. Os campos continuam sendo preenchidos inicialmente com os valores mockados e obtidos pela visão computacional, porém agora podem ser alterados caso o gestor identifique alguma inconsistência.

Além da edição dos campos, foi adicionado um indicador visual que informa quando existem alterações pendentes. Esse feedback permite que o gestor saiba que os dados exibidos diferem daqueles originalmente capturados pelo sistema, reduzindo a possibilidade de alterações não intencionais.

<div align="center">    
    <sup>Figura 1: Implementação dos campos editáveis</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1782437477/Captura_de_tela_de_2026-06-25_22-27-45_hv2cbi.png" />
    <sup>Fonte: Autores, 2026</sup>
</div>

### Fluxo de Utilização

O processo de validação passou a ocorrer da seguinte forma:

1. O gestor abre um match pendente na Central de Alertas.
2. A modal é carregada com os dados identificados automaticamente pelo sistema.
3. Caso sejam encontradas inconsistências, os campos podem ser editados.
4. Após a confirmação da aprovação ou rejeição, as alterações são enviadas ao backend juntamente com a decisão do gestor.
5. Os dados atualizados passam a representar as informações oficiais do registro validado.

Essa abordagem combina a velocidade proporcionada pela visão computacional com a capacidade de validação humana, aumentando a qualidade dos dados armazenados pelo sistema.

<div align="center">    
    <sup>Figura 2: Aviso de dados alterados</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1782437477/Captura_de_tela_de_2026-06-25_22-28-09_kjsqis.png" />
    <sup>Fonte: Autores, 2026</sup>
</div>

---

## Aba de Análises

Além das melhorias realizadas no processo de validação, foi desenvolvida uma nova aba denominada **Análises**, destinada a fornecer uma visão consolidada das informações registradas pela Central de Alertas.

O objetivo dessa funcionalidade é permitir que o gestor remoto acompanhe rapidamente o desempenho da operação por meio de indicadores e visualizações gráficas, reduzindo a necessidade de consultas individuais aos registros.

<div align="center">    
    <sup>Figura 3: Aba de análises</sup>
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1782437476/Captura_de_tela_de_2026-06-25_22-28-42_lwhwol.png" />
    <sup>Fonte: Autores, 2026</sup>
</div>

#### Indicadores

A interface apresenta cartões com informações resumidas sobre a operação, permitindo identificar rapidamente:

- quantidade total de matches registrados;
- número de matches pendentes;
- quantidade de aprovações;
- quantidade de recusas.

Esses indicadores facilitam o acompanhamento do fluxo operacional e auxiliam na identificação de possíveis gargalos durante o processo de validação.


#### Visualizações Gráficas

Além dos indicadores numéricos, a aba de análises apresenta gráficos que sintetizam as informações registradas pelo sistema.

Foram implementadas visualizações referentes à distribuição dos modelos de veículos identificados, à quantidade de matches gerados por drone e à evolução temporal dos registros. Esses gráficos permitem compreender padrões operacionais de maneira mais intuitiva e auxiliam na análise do comportamento do sistema ao longo do tempo.

---

## Benefícios das Alterações

As melhorias implementadas tornam a interface da Central de Alertas mais completa e adequada ao fluxo operacional da Pier.

Os campos editáveis permitem corrigir eventuais inconsistências identificadas durante a validação, aumentando a confiabilidade das informações armazenadas pelo sistema. Paralelamente, a nova aba de análises fornece uma visão consolidada da operação, permitindo acompanhar indicadores e identificar tendências de forma rápida e intuitiva.

Em conjunto, essas alterações tornam o processo de validação mais eficiente, melhoram a experiência do gestor remoto e estabelecem uma base sólida para futuras evoluções da plataforma.