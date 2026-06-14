export function ActionButton({ children, tone = 'blue', ...props }) {
  const toneClass =
    tone === 'red'
      ? 'bg-red-600 hover:bg-red-500'
      : tone === 'gray'
        ? 'bg-gray-700 hover:bg-gray-600'
        : 'bg-blue-600 hover:bg-blue-500'

  return (
    <button
      className={`${toneClass} px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50`}
      type="button"
      {...props}
    >
      {children}
    </button>
  )
}
