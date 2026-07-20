export default function TourSpotlight({ rect, stepIndex }) {
  if (!rect) {
    return null
  }

  return (
    <>
      <div className="local-tour-spotlight" style={rect} />
      <div
        className="local-tour-bubble"
        style={{
          left: rect.left + rect.width - 18,
          top: rect.top - 18,
        }}
      >
        {stepIndex + 1}
      </div>
    </>
  )
}
