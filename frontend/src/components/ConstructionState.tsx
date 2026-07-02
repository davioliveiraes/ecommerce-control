interface Props {
  title: string
  description: string
}

export function ConstructionState({ title, description }: Props) {
  return (
    <div className="relative border border-gray-200 bg-gray-50 px-10 py-16">
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage:
            'repeating-linear-gradient(135deg, var(--color-black) 0, var(--color-black) 1px, transparent 1px, transparent 14px)',
        }}
      />
      <div className="relative max-w-xl">
        <div className="kicker mb-5">Em construção</div>
        <h2 className="font-display text-3xl font-semibold text-black mb-3">
          {title}
        </h2>
        <p className="text-gray-600 leading-relaxed">{description}</p>
      </div>
    </div>
  )
}
