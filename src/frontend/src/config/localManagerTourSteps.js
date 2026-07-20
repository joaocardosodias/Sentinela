import batteryIcon from '../../img/onboarding/icons/battery.svg'
import connectivityIcon from '../../img/onboarding/icons/connectivity.svg'
import droneIdIcon from '../../img/onboarding/icons/drone-id.svg'
import liveSignalIcon from '../../img/onboarding/icons/live-signal.svg'
import locationIcon from '../../img/onboarding/icons/location.svg'
import mapIcon from '../../img/onboarding/icons/map.svg'
import noSignalIcon from '../../img/onboarding/icons/no-signal.svg'
import routeIcon from '../../img/onboarding/icons/route.svg'
import videoIcon from '../../img/onboarding/icons/video.svg'
import videoPreview from '../../img/onboarding/previews/step-01-video.png'
import telemetryPreview from '../../img/onboarding/previews/step-02-telemetria.png'
import mapPreview from '../../img/onboarding/previews/step-03-mapa.png'

export const localManagerTourSteps = [
  {
    id: 'local-video',
    title: 'Transmissão de vídeo',
    preview: videoPreview,
    targetSelector: '[data-tour="local-video"]',
    placement: 'bottom',
    bullets: [
      'Acompanhe a transmissão da câmera do drone em tempo real.',
      'Quando o servidor estiver indisponível, o painel informa que não há sinal.',
      'Use o vídeo para observar o ambiente durante a operação.',
    ],
    icons: [videoIcon, noSignalIcon, liveSignalIcon],
  },
  {
    id: 'local-telemetry',
    title: 'Dados de telemetria',
    preview: telemetryPreview,
    targetSelector: '[data-tour="local-telemetry"]',
    placement: 'left',
    bullets: [
      'Drone ID identifica o equipamento conectado à operação.',
      'Conectividade mostra a disponibilidade do enlace com o drone.',
      'Bateria indica a carga restante para acompanhar a segurança da missão.',
    ],
    icons: [droneIdIcon, connectivityIcon, batteryIcon],
  },
  {
    id: 'local-map',
    title: 'Mapa da operação',
    preview: mapPreview,
    targetSelector: '[data-tour="local-map"]',
    placement: 'top',
    bullets: [
      'O mapa apresenta a área acompanhada pelo gestor local.',
      'Relacione a posição do drone com o vídeo e os dados de telemetria.',
      'Acompanhe rota, destino e deslocamento durante a missão.',
    ],
    icons: [mapIcon, locationIcon, routeIcon],
  },
]
