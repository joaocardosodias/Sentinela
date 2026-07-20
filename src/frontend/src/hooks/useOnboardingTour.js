import { useEffect, useMemo, useState } from 'react'
import { onboardingSteps } from '../config/onboardingSteps.js'

const STORAGE_KEY = 'pier:onboarding-tour-completed'

export function useOnboardingTour(onNavigate, enabled = true) {
  const [isOpen, setIsOpen] = useState(() => enabled && localStorage.getItem(STORAGE_KEY) !== 'true')
  const [stepIndex, setStepIndex] = useState(0)

  const step = onboardingSteps[stepIndex]

  useEffect(() => {
    if (enabled && !isOpen && localStorage.getItem(STORAGE_KEY) !== 'true') {
      setIsOpen(true)
    }
  }, [enabled, isOpen])

  useEffect(() => {
    if (enabled && isOpen && step?.page) {
      onNavigate(step.page)
    }
  }, [enabled, isOpen, onNavigate, step?.page])

  const controls = useMemo(() => {
    function finish() {
      localStorage.setItem(STORAGE_KEY, 'true')
      setIsOpen(false)
    }

    return {
      next() {
        setStepIndex((current) => {
          if (current >= onboardingSteps.length - 1) {
            finish()
            return current
          }

          return current + 1
        })
      },
      previous() {
        setStepIndex((current) => Math.max(0, current - 1))
      },
      close: finish,
      restart() {
        localStorage.removeItem(STORAGE_KEY)
        setStepIndex(0)
        setIsOpen(true)
      },
    }
  }, [])

  return {
    isOpen,
    step,
    stepIndex,
    totalSteps: onboardingSteps.length,
    ...controls,
  }
}
