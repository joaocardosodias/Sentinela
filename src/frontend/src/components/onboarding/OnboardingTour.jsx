import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import TourConnector from './TourConnector.jsx'
import TourPopover from './TourPopover.jsx'
import './onboarding.css'

const TARGET_PADDING = 10
const POPOVER_WIDTH = 760
const EDGE_GAP = 18

export default function OnboardingTour({
  isOpen,
  step,
  stepIndex,
  totalSteps,
  onPrevious,
  onNext,
  onClose,
}) {
  const popoverRef = useRef(null)
  const [targetRect, setTargetRect] = useState(null)
  const [popoverRect, setPopoverRect] = useState(null)
  const [viewport, setViewport] = useState(() => ({
    width: window.innerWidth,
    height: window.innerHeight,
  }))

  useEffect(() => {
    if (!isOpen || !step) {
      return undefined
    }

    let attempts = 0
    const interval = window.setInterval(() => {
      attempts += 1
      const target = document.querySelector(step.targetSelector)

      if (target) {
        target.scrollIntoView({ block: 'center', inline: 'center', behavior: 'smooth' })
        measureTarget(step.targetSelector, setTargetRect)
        measurePopover(popoverRef.current, setPopoverRect)
        window.clearInterval(interval)
      }

      if (attempts >= 20) {
        window.clearInterval(interval)
      }
    }, 180)

    const timeout = window.setTimeout(() => {
      measureTarget(step.targetSelector, setTargetRect)
      measurePopover(popoverRef.current, setPopoverRect)
    }, 280)

    return () => {
      window.clearInterval(interval)
      window.clearTimeout(timeout)
    }
  }, [isOpen, step])

  useLayoutEffect(() => {
    if (!isOpen || !step) {
      return undefined
    }

    function handleMeasure() {
      setViewport({ width: window.innerWidth, height: window.innerHeight })
      measureTarget(step.targetSelector, setTargetRect)
      measurePopover(popoverRef.current, setPopoverRect)
    }

    handleMeasure()
    window.addEventListener('resize', handleMeasure)
    window.addEventListener('scroll', handleMeasure, true)

    return () => {
      window.removeEventListener('resize', handleMeasure)
      window.removeEventListener('scroll', handleMeasure, true)
    }
  }, [isOpen, step])

  const paddedTarget = useMemo(() => {
    if (!targetRect) {
      return null
    }

    return {
      top: Math.max(EDGE_GAP, targetRect.top - TARGET_PADDING),
      left: Math.max(EDGE_GAP, targetRect.left - TARGET_PADDING),
      width: Math.min(viewport.width - EDGE_GAP * 2, targetRect.width + TARGET_PADDING * 2),
      height: Math.min(viewport.height - EDGE_GAP * 2, targetRect.height + TARGET_PADDING * 2),
    }
  }, [targetRect, viewport])

  const popoverPosition = useMemo(() => {
    return getPopoverPosition(step, paddedTarget, viewport)
  }, [paddedTarget, step, viewport])

  useLayoutEffect(() => {
    if (isOpen) {
      measurePopover(popoverRef.current, setPopoverRect)
    }
  }, [isOpen, popoverPosition.left, popoverPosition.top])

  if (!isOpen || !step) {
    return null
  }

  return (
    <div className="tour-layer">
      <div className="tour-overlay tour-overlay--top" style={overlayTop(paddedTarget)} />
      <div className="tour-overlay tour-overlay--right" style={overlayRight(paddedTarget, viewport)} />
      <div className="tour-overlay tour-overlay--bottom" style={overlayBottom(paddedTarget, viewport)} />
      <div className="tour-overlay tour-overlay--left" style={overlayLeft(paddedTarget)} />

      {paddedTarget && (
        <>
          <div className="tour-highlight" style={paddedTarget} />
          <div className="tour-target-bubble" style={bubblePosition(paddedTarget)}>
            {stepIndex + 1}
          </div>
        </>
      )}

      <TourConnector targetRect={paddedTarget} popoverRect={popoverRect} />

      <TourPopover
        step={step}
        stepIndex={stepIndex}
        totalSteps={totalSteps}
        position={popoverPosition}
        onPrevious={onPrevious}
        onNext={onNext}
        onClose={onClose}
        popoverRef={popoverRef}
      />
    </div>
  )
}

function measureTarget(selector, setTargetRect) {
  const target = document.querySelector(selector)
  setTargetRect(target ? target.getBoundingClientRect() : null)
}

function measurePopover(element, setPopoverRect) {
  setPopoverRect(element ? element.getBoundingClientRect() : null)
}

function getPopoverPosition(step, targetRect, viewport) {
  const width = Math.min(POPOVER_WIDTH, viewport.width - EDGE_GAP * 2)
  const estimatedHeight = viewport.width < 720 ? 620 : 430

  if (!targetRect) {
    return {
      left: (viewport.width - width) / 2,
      top: Math.max(EDGE_GAP, (viewport.height - estimatedHeight) / 2),
      caret: 'none',
    }
  }

  if (viewport.width < 820) {
    return {
      left: EDGE_GAP,
      top: clamp(targetRect.bottom + 18, EDGE_GAP, viewport.height - estimatedHeight - EDGE_GAP),
      caret: 'top',
    }
  }

  const placement = step.placement || 'bottom'
  const centerX = targetRect.left + targetRect.width / 2
  const centerY = targetRect.top + targetRect.height / 2

  if (placement === 'left') {
    const left = targetRect.left - width - 24
    if (left >= EDGE_GAP) {
      return {
        left,
        top: clamp(centerY - estimatedHeight / 2, EDGE_GAP, viewport.height - estimatedHeight - EDGE_GAP),
        caret: 'right',
      }
    }

    return {
      left: clamp(targetRect.right + 24, EDGE_GAP, viewport.width - width - EDGE_GAP),
      top: clamp(centerY - estimatedHeight / 2, EDGE_GAP, viewport.height - estimatedHeight - EDGE_GAP),
      caret: 'left',
    }
  }

  return {
    left: clamp(centerX - width / 2, EDGE_GAP, viewport.width - width - EDGE_GAP),
    top: clamp(targetRect.bottom + 24, EDGE_GAP, viewport.height - estimatedHeight - EDGE_GAP),
    caret: 'top',
  }
}

function overlayTop(target) {
  if (!target) {
    return { inset: 0 }
  }

  return { left: 0, top: 0, width: '100vw', height: target.top }
}

function overlayRight(target, viewport) {
  if (!target) {
    return { display: 'none' }
  }

  return {
    left: target.left + target.width,
    top: target.top,
    width: Math.max(0, viewport.width - target.left - target.width),
    height: target.height,
  }
}

function overlayBottom(target, viewport) {
  if (!target) {
    return { display: 'none' }
  }

  return {
    left: 0,
    top: target.top + target.height,
    width: '100vw',
    height: Math.max(0, viewport.height - target.top - target.height),
  }
}

function overlayLeft(target) {
  if (!target) {
    return { display: 'none' }
  }

  return {
    left: 0,
    top: target.top,
    width: target.left,
    height: target.height,
  }
}

function bubblePosition(target) {
  return {
    left: target.left + target.width - 14,
    top: target.top - 14,
  }
}

function clamp(value, min, max) {
  if (max < min) {
    return min
  }

  return Math.min(Math.max(value, min), max)
}
