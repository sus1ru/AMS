export function DataTable({ columns, rows, emptyLabel }) {
  return (
    <div className="overflow-x-auto border border-gray-800">
      <table className="w-full min-w-[720px] border-collapse text-left text-sm">
        <thead className="bg-gray-950 text-xs uppercase text-gray-400">
          <tr>
            {columns.map((column) => (
              <th className="border-b border-gray-800 px-3 py-2 font-semibold" key={column.key}>
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td className="px-3 py-8 text-center text-gray-500" colSpan={columns.length}>
                {emptyLabel}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr className="border-t border-gray-800" key={row.id}>
                {columns.map((column) => (
                  <td className="px-3 py-2 text-gray-200" key={column.key}>
                    {column.render ? column.render(row) : (row[column.key] ?? '-')}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
