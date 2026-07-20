import { useState } from 'react'
import Login from './screens/Login.jsx'
import OperationsManager from './screens/OperationsManager.jsx'
import AlertCenter from './screens/AlertCenter.jsx'
import AcceptedVehicles from './screens/AcceptedVehicles.jsx'
import RejectedVehicles from './screens/RejectedVehicles.jsx'
import Analytics from './screens/Analytics.jsx'
import OnboardingTour from './components/onboarding/OnboardingTour.jsx'
import LocalManagerTour from './components/onboarding/LocalManagerTour.jsx'
import { useOnboardingTour } from './hooks/useOnboardingTour.js'
import { useLocalManagerTour } from './hooks/useLocalManagerTour.js'

const PIER_SCREENS = ['alerts', 'accepted', 'rejected']

export default function App() {
  const [screen, setScreen] = useState(() => {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')

    if (!token) {
      return 'login'
    }

    return role === 'gestor_local' ? 'operations' : 'alerts'
  })
  const isPierScreen = PIER_SCREENS.includes(screen)
  const tour = useOnboardingTour(setScreen, isPierScreen)
  const localManagerTour = useLocalManagerTour(screen === 'operations')

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    setScreen('login')
  }

  return (
    <>
      {screen === 'login' && <Login onLogin={setScreen} />}
      {screen === 'operations' && (
        <OperationsManager onLogout={handleLogout} />
      )}
      {screen === 'alerts' && (
        <AlertCenter
          onLogout={handleLogout}
          onNavigate={setScreen}
          currentScreen={screen}
          activeTourStep={tour.isOpen ? tour.step : null}
        />
      )}
      {screen === 'accepted' && (
        <AcceptedVehicles
          onLogout={handleLogout}
          onNavigate={setScreen}
          currentScreen={screen}
          activeTourStep={tour.isOpen ? tour.step : null}
        />
      )}
      {screen === 'rejected' && (
        <RejectedVehicles
          onLogout={handleLogout}
          onNavigate={setScreen}
          currentScreen={screen}
          activeTourStep={tour.isOpen ? tour.step : null}
        />
      )}
      {screen === 'analytics' && (
        <Analytics
          onLogout={handleLogout}
          onNavigate={setScreen}
          currentScreen={screen}
        />
      )}
      <OnboardingTour
        isOpen={tour.isOpen && isPierScreen}
        step={tour.step}
        stepIndex={tour.stepIndex}
        totalSteps={tour.totalSteps}
        onPrevious={tour.previous}
        onNext={tour.next}
        onClose={tour.close}
      />
      <LocalManagerTour
        isOpen={localManagerTour.isOpen && screen === 'operations'}
        step={localManagerTour.step}
        stepIndex={localManagerTour.stepIndex}
        totalSteps={localManagerTour.totalSteps}
        onPrevious={localManagerTour.previous}
        onNext={localManagerTour.next}
        onClose={localManagerTour.close}
      />
    </>
  )
}
