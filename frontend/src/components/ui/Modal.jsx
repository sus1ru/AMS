export function Modal({ children, onClose, title }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="w-full max-w-4xl border border-gray-800 bg-gray-950 shadow-2xl">
        <div className="flex items-center justify-between border-b border-gray-800 px-5 py-4">
          <h3 className="text-base font-semibold text-white">{title}</h3>
          <button
            className="px-2 py-1 text-xl leading-none text-gray-400 hover:text-white"
            onClick={onClose}
            type="button"
          >
            &times;
          </button>
        </div>
        <div className="max-h-[80vh] overflow-y-auto p-5">{children}</div>
      </div>
    </div>
  )
}
