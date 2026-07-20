export default function TourConnector({ targetRect, popoverRect }) {
  if (!targetRect || !popoverRect) {
    return null
  }

  const startX = popoverRect.left + popoverRect.width / 2
  const startY = popoverRect.top + popoverRect.height / 2
  const endX = targetRect.left + targetRect.width / 2
  const endY = targetRect.top + targetRect.height / 2
  const minX = Math.min(startX, endX)
  const minY = Math.min(startY, endY)
  const width = Math.abs(endX - startX) || 1
  const height = Math.abs(endY - startY) || 1
  const x1 = startX - minX
  const y1 = startY - minY
  const x2 = endX - minX
  const y2 = endY - minY

  return (
    <svg
      className="tour-connector"
      style={{
        left: minX,
        top: minY,
        width,
        height,
      }}
      viewBox={`0 0 ${width} ${height}`}
      aria-hidden="true"
    >
      <defs>
        <marker
          id="tour-connector-arrow"
          markerWidth="8"
          markerHeight="8"
          refX="7"
          refY="4"
          orient="auto"
        >
          <path d="M0,0 L8,4 L0,8 Z" fill="#FF3465" />
        </marker>
      </defs>
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke="#FF3465"
        strokeWidth="2"
        strokeDasharray="6 7"
        markerEnd="url(#tour-connector-arrow)"
      />
    </svg>
  )
}
