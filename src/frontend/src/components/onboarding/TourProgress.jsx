export default function TourProgress({ current, total }) {
  return (
    <div className="tour-progress" aria-label={`Etapa ${current + 1} de ${total}`}>
      {Array.from({ length: total }).map((_, index) => (
        <span
          key={index}
          className={index === current ? 'tour-progress__dot is-active' : 'tour-progress__dot'}
        />
      ))}
    </div>
  )
}
