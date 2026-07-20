import bellIcon from '../../img/onboarding/icons/bell.svg'
import carIcon from '../../img/onboarding/icons/car.svg'
import clockIcon from '../../img/onboarding/icons/clock.svg'
import cursorIcon from '../../img/onboarding/icons/cursor.svg'
import imageIcon from '../../img/onboarding/icons/image.svg'
import rejectIcon from '../../img/onboarding/icons/reject.svg'
import shieldCheckIcon from '../../img/onboarding/icons/shield-check.svg'
import step01Preview from '../../img/onboarding/previews/step-01-central-alertas.png'
import step02Preview from '../../img/onboarding/previews/step-02-verificacao-alerta.png'
import step03Preview from '../../img/onboarding/previews/step-03-veiculos-confirmados.png'
import step04Preview from '../../img/onboarding/previews/step-04-detalhe-confirmado.png'
import step05Preview from '../../img/onboarding/previews/step-05-veiculos-recusados.png'
import step06Preview from '../../img/onboarding/previews/step-06-detalhe-recusado.png'

export const onboardingSteps = [
  {
    id: 'central-alertas',
    page: 'alerts',
    title: 'Central de Alertas',
    preview: step01Preview,
    targetSelector: '[data-tour="alert-card-first"]',
    placement: 'bottom',
    bullets: [
      'Aqui aparecem os matches suspeitos identificados pelo sistema.',
      'Cada card mostra placa, horário, localização, modelo e cor.',
      'Selecione um card para abrir a verificação detalhada.',
    ],
    icons: [
      bellIcon,
      carIcon,
      cursorIcon,
    ],
  },
  {
    id: 'verificacao-alerta',
    page: 'alerts',
    title: 'Verificação do Alerta',
    preview: step02Preview,
    targetSelector: '[data-tour="alert-decision"]',
    placement: 'left',
    openMode: 'alert-decision',
    bullets: [
      'Confira a imagem capturada antes de validar o alerta.',
      'Compare placa, modelo, cor e localização com os dados do sistema.',
      'Use as ações para aceitar o resgate ou recusar a ocorrência.',
    ],
    icons: [
      imageIcon,
      carIcon,
      shieldCheckIcon,
    ],
  },
  {
    id: 'veiculos-confirmados',
    page: 'accepted',
    title: 'Veículos Confirmados',
    preview: step03Preview,
    targetSelector: '[data-tour="confirmed-card-first"]',
    placement: 'bottom',
    bullets: [
      'Os alertas aceitos passam a compor a lista de veículos confirmados.',
      'Cada card resume os dados principais para acompanhamento rápido.',
      'Selecione um card para consultar o detalhe completo do confirmado.',
    ],
    icons: [
      shieldCheckIcon,
      carIcon,
      cursorIcon,
    ],
  },
  {
    id: 'detalhes-confirmado',
    page: 'accepted',
    title: 'Detalhes do Confirmado',
    preview: step04Preview,
    targetSelector: '[data-tour="confirmed-detail"]',
    placement: 'left',
    openMode: 'confirmed-detail',
    bullets: [
      'A visualização amplia a imagem relacionada ao veículo confirmado.',
      'Os dados ficam organizados para auditoria e conferência operacional.',
      'O horário de validação ajuda a rastrear quando o resgate foi aprovado.',
    ],
    icons: [
      imageIcon,
      carIcon,
      shieldCheckIcon,
    ],
  },
  {
    id: 'veiculos-recusados',
    page: 'rejected',
    title: 'Veículos Recusados',
    preview: step05Preview,
    targetSelector: '[data-tour="rejected-card-first"]',
    placement: 'bottom',
    bullets: [
      'Alertas descartados ficam separados para consulta posterior.',
      'A lista preserva placa, horário, drone e localização da leitura.',
      'Selecione um card para revisar o motivo operacional do descarte.',
    ],
    icons: [
      rejectIcon,
      carIcon,
      cursorIcon,
    ],
  },
  {
    id: 'detalhes-recusado',
    page: 'rejected',
    title: 'Detalhes do Recusado',
    preview: step06Preview,
    targetSelector: '[data-tour="rejected-detail"]',
    placement: 'left',
    openMode: 'rejected-detail',
    bullets: [
      'O detalhe mantém a imagem e os dados usados na análise.',
      'A marcação de recusa diferencia esses registros dos confirmados.',
      'O horário registrado apoia conferências futuras da operação.',
    ],
    icons: [
      imageIcon,
      carIcon,
      clockIcon,
    ],
  },
]
