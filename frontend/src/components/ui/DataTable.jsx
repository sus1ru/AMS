function PaginationControls({ pagination }) {
  if (!pagination) {
    return null
  }

  const { limit, onPageChange, page, total } = pagination
  const totalPages = Math.max(1, Math.ceil(total / limit))
  const start = total === 0 ? 0 : (page - 1) * limit + 1
  const end = Math.min(page * limit, total)

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-gray-800 bg-gray-950 px-3 py-3 text-sm text-gray-300">
      <span>
        Showing {start}-{end} of {total}
      </span>
      <div className="flex items-center gap-2">
        <button
          className="border border-gray-700 px-3 py-1 text-white disabled:cursor-not-allowed disabled:opacity-50"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          type="button"
        >
          Previous
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button
          className="border border-gray-700 px-3 py-1 text-white disabled:cursor-not-allowed disabled:opacity-50"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          type="button"
        >
          Next
        </button>
      </div>
    </div>
  )
}

export function DataTable({ columns, emptyLabel, pagination, rows }) {
  return (
    <div className="border border-gray-800">
      <div className="overflow-x-auto">
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
      <PaginationControls pagination={pagination} />
    </div>
  )
}
