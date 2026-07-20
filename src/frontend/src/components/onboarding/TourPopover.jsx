import TourProgress from './TourProgress.jsx'

export default function TourPopover({
  step,
  stepIndex,
  totalSteps,
  position,
  onPrevious,
  onNext,
  onClose,
  popoverRef,
}) {
  const isLast = stepIndex === totalSteps - 1

  return (
    <article
      ref={popoverRef}
      className={`tour-popover tour-popover--${position.caret}`}
      style={{ left: position.left, top: position.top }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="tour-title"
    >
      <div className="tour-popover__header">
        <span className="tour-popover__badge">PASSO {stepIndex + 1} DE {totalSteps}</span>
        <button className="tour-popover__close" type="button" aria-label="Fechar onboarding" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="tour-popover__body">
        <div className="tour-popover__preview-wrap">
          <img className="tour-popover__preview" src={step.preview} alt="" />
        </div>

        <div className="tour-popover__content">
          <h2 id="tour-title">{step.title}</h2>
          <div className="tour-popover__instructions">
            {step.bullets.map((text, index) => (
              <div className="tour-popover__instruction" key={text}>
                <span className="tour-popover__icon-bubble">
                  <img src={step.icons[index]} alt="" />
                </span>
                <p>{text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="tour-popover__divider" />

      <div className="tour-popover__footer">
        <button className="tour-popover__button tour-popover__button--ghost" type="button" onClick={onPrevious} disabled={stepIndex === 0}>
          <span aria-hidden="true">←</span>
          Voltar
        </button>

        <TourProgress current={stepIndex} total={totalSteps} />

        <button className="tour-popover__button tour-popover__button--primary" type="button" onClick={onNext}>
          {isLast ? 'Concluir' : 'Próximo'}
          {!isLast && <span aria-hidden="true">→</span>}
        </button>
      </div>
    </article>
  )
}
