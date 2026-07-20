import { useCallback, useEffect, useMemo, useState } from 'react'
import { localManagerTourSteps } from '../config/localManagerTourSteps.js'

const STORAGE_KEY = 'pier:local-manager:onboarding:v1'

export function useLocalManagerTour(enabled) {
  const shouldForceTour = useMemo(() => {
    return new URLSearchParams(window.location.search).get('tour') === '1'
  }, [])

  const [isOpen, setIsOpen] = useState(() => {
    if (!enabled) return false
    if (shouldForceTour) return true
    return !localStorage.getItem(STORAGE_KEY)
  })
  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    if (!enabled) {
      setIsOpen(false)
      return
    }

    if (shouldForceTour || !localStorage.getItem(STORAGE_KEY)) {
      setIsOpen(true)
    }
  }, [enabled, shouldForceTour])

  const close = useCallback(() => {
    localStorage.setItem(STORAGE_KEY, 'dismissed')
    setIsOpen(false)
  }, [])

  const finish = useCallback(() => {
    localStorage.setItem(STORAGE_KEY, 'completed')
    setIsOpen(false)
  }, [])

  const next = useCallback(() => {
    setStepIndex((current) => {
      if (current >= localManagerTourSteps.length - 1) {
        finish()
        return current
      }

      return current + 1
    })
  }, [finish])

  const previous = useCallback(() => {
    setStepIndex((current) => Math.max(0, current - 1))
  }, [])

  return {
    isOpen,
    step: localManagerTourSteps[stepIndex],
    stepIndex,
    totalSteps: localManagerTourSteps.length,
    close,
    next,
    previous,
  }
}
