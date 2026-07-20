import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import TourSpotlight from './TourSpotlight.jsx'
import './localManagerTour.css'

const TARGET_PADDING = 8
const EDGE_GAP = 24
const DESKTOP_POPOVER_WIDTH = 1180
const DESKTOP_POPOVER_HEIGHT = 590

export default function LocalManagerTour({
  isOpen,
  step,
  stepIndex,
  totalSteps,
  onPrevious,
  onNext,
  onClose,
}) {
  const popoverRef = useRef(null)
  const previousFocusRef = useRef(null)
  const [targetRect, setTargetRect] = useState(null)
  const [popoverRect, setPopoverRect] = useState(null)
  const [viewport, setViewport] = useState(() => ({
    width: window.innerWidth,
    height: window.innerHeight,
  }))

  const paddedTarget = useMemo(() => {
    if (!targetRect) return null

    return {
      left: Math.max(EDGE_GAP, targetRect.left - TARGET_PADDING),
      top: Math.max(EDGE_GAP, targetRect.top - TARGET_PADDING),
      width: Math.min(viewport.width - EDGE_GAP * 2, targetRect.width + TARGET_PADDING * 2),
      height: Math.min(viewport.height - EDGE_GAP * 2, targetRect.height + TARGET_PADDING * 2),
    }
  }, [targetRect, viewport])

  const popoverPosition = useMemo(() => {
    return getPopoverPosition(step, paddedTarget, viewport)
  }, [paddedTarget, step, viewport])

  const caret = useMemo(() => {
    return getCaretPosition(popoverRect, paddedTarget)
  }, [popoverRect, paddedTarget])

  useEffect(() => {
    if (!isOpen) return undefined

    previousFocusRef.current = document.activeElement
    window.setTimeout(() => popoverRef.current?.focus(), 0)

    return () => {
      if (previousFocusRef.current && typeof previousFocusRef.current.focus === 'function') {
        previousFocusRef.current.focus()
      }
    }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen || !step) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
        return
      }

      if (event.key === 'ArrowRight') {
        event.preventDefault()
        onNext()
        return
      }

      if (event.key === 'ArrowLeft') {
        event.preventDefault()
        if (stepIndex > 0) onPrevious()
        return
      }

      if (event.key === 'Tab') {
        trapFocus(event, popoverRef.current)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose, onNext, onPrevious, step, stepIndex])

  useEffect(() => {
    if (!isOpen || !step) return undefined

    const target = document.querySelector(step.targetSelector)
    if (target) {
      target.scrollIntoView({
        block: step.id === 'local-map' ? 'center' : 'nearest',
        inline: 'nearest',
        behavior: 'smooth',
      })
    }

    let raf = 0
    const measure = () => {
      window.cancelAnimationFrame(raf)
      raf = window.requestAnimationFrame(() => {
        setViewport({ width: window.innerWidth, height: window.innerHeight })
        setTargetRect(readRect(step.targetSelector))
        setPopoverRect(popoverRef.current?.getBoundingClientRect() || null)
      })
    }

    const resizeObserver = new ResizeObserver(measure)
    const observedTarget = document.querySelector(step.targetSelector)
    if (observedTarget) resizeObserver.observe(observedTarget)
    if (popoverRef.current) resizeObserver.observe(popoverRef.current)
    resizeObserver.observe(document.body)

    const timeouts = [80, 220, 480, 820].map((delay) => window.setTimeout(measure, delay))
    window.addEventListener('resize', measure)
    window.addEventListener('scroll', measure, true)
    measure()

    return () => {
      window.cancelAnimationFrame(raf)
      timeouts.forEach((timeout) => window.clearTimeout(timeout))
      resizeObserver.disconnect()
      window.removeEventListener('resize', measure)
      window.removeEventListener('scroll', measure, true)
    }
  }, [isOpen, step])

  useLayoutEffect(() => {
    if (isOpen) {
      setPopoverRect(popoverRef.current?.getBoundingClientRect() || null)
    }
  }, [isOpen, popoverPosition.left, popoverPosition.top])

  if (!isOpen || !step) {
    return null
  }

  return (
    <div className="local-tour-layer">
      <Overlay target={paddedTarget} viewport={viewport} />
      <TourSpotlight rect={paddedTarget} stepIndex={stepIndex} />
      <Connector targetRect={paddedTarget} popoverRect={popoverRect} />
      <LocalTourPopover
        refElement={popoverRef}
        step={step}
        stepIndex={stepIndex}
        totalSteps={totalSteps}
        position={popoverPosition}
        caret={caret}
        onPrevious={onPrevious}
        onNext={onNext}
        onClose={onClose}
      />
    </div>
  )
}

function LocalTourPopover({
  refElement,
  step,
  stepIndex,
  totalSteps,
  position,
  caret,
  onPrevious,
  onNext,
  onClose,
}) {
  const isLast = stepIndex === totalSteps - 1
  const descriptionId = `local-tour-desc-${step.id}`

  return (
    <article
      ref={refElement}
      className={`local-tour-popover local-tour-popover--${position.caret}`}
      style={{
        left: position.left,
        top: position.top,
        '--local-caret-x': caret.x,
        '--local-caret-y': caret.y,
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="local-tour-title"
      aria-describedby={descriptionId}
      tabIndex={-1}
    >
      <div className="local-tour-header">
        <span className="local-tour-badge">PASSO {stepIndex + 1} DE {totalSteps}</span>
        <button className="local-tour-close" type="button" aria-label="Fechar onboarding" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="local-tour-body">
        <div className="local-tour-preview-shell">
          <img className="local-tour-preview" src={step.preview} alt="" />
        </div>

        <div className="local-tour-content">
          <h2 id="local-tour-title">{step.title}</h2>
          <p id={descriptionId} className="local-tour-description">
            Etapa {stepIndex + 1} de {totalSteps}: {step.title}
          </p>
          <div className="local-tour-instructions">
            {step.bullets.map((text, index) => (
              <div className="local-tour-instruction" key={text}>
                <span className="local-tour-icon-bubble">
                  <img src={step.icons[index]} alt="" aria-hidden="true" />
                </span>
                <p>{text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="local-tour-divider" />

      <footer className="local-tour-footer">
        <button
          className="local-tour-button local-tour-button--ghost"
          type="button"
          onClick={onPrevious}
          disabled={stepIndex === 0}
        >
          <span aria-hidden="true">←</span>
          Voltar
        </button>

        <div className="local-tour-progress" aria-label={`Etapa ${stepIndex + 1} de ${totalSteps}`}>
          {Array.from({ length: totalSteps }).map((_, index) => (
            <span
              key={index}
              className={index === stepIndex ? 'local-tour-progress-dot is-active' : 'local-tour-progress-dot'}
            />
          ))}
        </div>

        <button className="local-tour-button local-tour-button--primary" type="button" onClick={onNext}>
          {isLast ? 'Concluir' : 'Próximo'}
          <span aria-hidden="true">→</span>
        </button>
      </footer>
    </article>
  )
}

function Connector({ targetRect, popoverRect }) {
  if (!targetRect || !popoverRect || window.innerWidth < 820) {
    return null
  }

  const targetPoint = {
    x: targetRect.left + targetRect.width / 2,
    y: targetRect.top + targetRect.height / 2,
  }
  const startPoint = closestPopoverEdgePoint(popoverRect, targetPoint)
  const controlPoint = {
    x: (startPoint.x + targetPoint.x) / 2,
    y: Math.min(startPoint.y, targetPoint.y) - 48,
  }
  const path = `M ${startPoint.x} ${startPoint.y} Q ${controlPoint.x} ${controlPoint.y} ${targetPoint.x} ${targetPoint.y}`

  return (
    <svg className="local-tour-connector" aria-hidden="true">
      <defs>
        <marker
          id="local-tour-arrow"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="5"
          orient="auto"
        >
          <path d="M0,0 L10,5 L0,10 Z" fill="#FF3465" />
        </marker>
      </defs>
      <path
        d={path}
        fill="none"
        stroke="#FF3465"
        strokeWidth="2.5"
        strokeDasharray="8 8"
        markerEnd="url(#local-tour-arrow)"
      />
    </svg>
  )
}

function Overlay({ target, viewport }) {
  if (!target) {
    return <div className="local-tour-overlay" style={{ inset: 0 }} />
  }

  return (
    <>
      <div className="local-tour-overlay" style={{ left: 0, top: 0, width: '100vw', height: target.top }} />
      <div
        className="local-tour-overlay"
        style={{
          left: target.left + target.width,
          top: target.top,
          width: Math.max(0, viewport.width - target.left - target.width),
          height: target.height,
        }}
      />
      <div
        className="local-tour-overlay"
        style={{
          left: 0,
          top: target.top + target.height,
          width: '100vw',
          height: Math.max(0, viewport.height - target.top - target.height),
        }}
      />
      <div
        className="local-tour-overlay"
        style={{
          left: 0,
          top: target.top,
          width: target.left,
          height: target.height,
        }}
      />
    </>
  )
}

function readRect(selector) {
  const element = document.querySelector(selector)
  return element ? element.getBoundingClientRect() : null
}

function getPopoverPosition(step, targetRect, viewport) {
  const width = Math.min(DESKTOP_POPOVER_WIDTH, viewport.width - EDGE_GAP * 2)
  const height = viewport.width < 820 ? Math.min(720, viewport.height - EDGE_GAP * 2) : DESKTOP_POPOVER_HEIGHT

  if (!targetRect) {
    return {
      left: (viewport.width - width) / 2,
      top: Math.max(EDGE_GAP, (viewport.height - height) / 2),
      caret: 'none',
    }
  }

  if (viewport.width < 820) {
    return {
      left: 14,
      top: clamp(targetRect.bottom + 18, 14, viewport.height - height - 14),
      caret: 'top',
    }
  }

  const centerX = targetRect.left + targetRect.width / 2
  const centerY = targetRect.top + targetRect.height / 2
  const placement = step.placement || 'bottom'

  if (placement === 'left') {
    const left = targetRect.left - width - 28
    if (left >= EDGE_GAP) {
      return {
        left,
        top: clamp(centerY - height / 2, EDGE_GAP, viewport.height - height - EDGE_GAP),
        caret: 'right',
      }
    }

    return {
      left: clamp(targetRect.right + 28, EDGE_GAP, viewport.width - width - EDGE_GAP),
      top: clamp(centerY - height / 2, EDGE_GAP, viewport.height - height - EDGE_GAP),
      caret: 'left',
    }
  }

  if (placement === 'top') {
    const top = targetRect.top - height - 28
    if (top >= EDGE_GAP) {
      return {
        left: clamp(centerX - width / 2, EDGE_GAP, viewport.width - width - EDGE_GAP),
        top,
        caret: 'bottom',
      }
    }
  }

  return {
    left: clamp(centerX - width / 2, EDGE_GAP, viewport.width - width - EDGE_GAP),
    top: clamp(targetRect.bottom + 28, EDGE_GAP, viewport.height - height - EDGE_GAP),
    caret: 'top',
  }
}

function getCaretPosition(popoverRect, targetRect) {
  if (!popoverRect || !targetRect) {
    return { x: '50%', y: '50%' }
  }

  const targetCenterX = targetRect.left + targetRect.width / 2
  const targetCenterY = targetRect.top + targetRect.height / 2

  return {
    x: `${clamp(targetCenterX - popoverRect.left, 34, popoverRect.width - 34)}px`,
    y: `${clamp(targetCenterY - popoverRect.top, 34, popoverRect.height - 34)}px`,
  }
}

function closestPopoverEdgePoint(popoverRect, point) {
  const leftDistance = Math.abs(point.x - popoverRect.left)
  const rightDistance = Math.abs(point.x - popoverRect.right)
  const topDistance = Math.abs(point.y - popoverRect.top)
  const bottomDistance = Math.abs(point.y - popoverRect.bottom)
  const min = Math.min(leftDistance, rightDistance, topDistance, bottomDistance)

  if (min === leftDistance) {
    return { x: popoverRect.left, y: clamp(point.y, popoverRect.top + 28, popoverRect.bottom - 28) }
  }

  if (min === rightDistance) {
    return { x: popoverRect.right, y: clamp(point.y, popoverRect.top + 28, popoverRect.bottom - 28) }
  }

  if (min === topDistance) {
    return { x: clamp(point.x, popoverRect.left + 28, popoverRect.right - 28), y: popoverRect.top }
  }

  return { x: clamp(point.x, popoverRect.left + 28, popoverRect.right - 28), y: popoverRect.bottom }
}

function trapFocus(event, root) {
  if (!root) return

  const focusable = Array.from(
    root.querySelectorAll('button:not([disabled]), [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')
  )

  if (focusable.length === 0) return

  const first = focusable[0]
  const last = focusable[focusable.length - 1]

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
    return
  }

  if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

function clamp(value, min, max) {
  if (max < min) return min
  return Math.min(Math.max(value, min), max)
}
