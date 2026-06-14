export function TextInput({ label, name, type = 'text', value, onChange, required = true, ...props }) {
  return (
    <div className="text-left">
      <label className="mb-1 block text-sm text-gray-300">{label}</label>
      <input
        className="w-full border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-blue-500"
        name={name}
        onChange={onChange}
        required={required}
        type={type}
        value={value}
        {...props}
      />
    </div>
  )
}

export function SelectInput({ label, name, value, onChange, children, required = true, ...props }) {
  return (
    <div className="text-left">
      <label className="mb-1 block text-sm text-gray-300">{label}</label>
      <select
        className="w-full border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-blue-500"
        name={name}
        onChange={onChange}
        required={required}
        value={value}
        {...props}
      >
        {children}
      </select>
    </div>
  )
}
