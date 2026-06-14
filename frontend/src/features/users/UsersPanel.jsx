import { useEffect, useState } from 'react'
import { ActionButton } from '../../components/ui/ActionButton'
import { DataTable } from '../../components/ui/DataTable'
import { usersApi } from '../../lib/api'
import { UserCreateForm } from './UserCreateForm'

export function UsersPanel({ onError }) {
  const [users, setUsers] = useState([])
  const [page, setPage] = useState(1)
  const [pagination, setPagination] = useState({ total: 0 })
  const [loading, setLoading] = useState(false)

  async function loadUsers(nextPage = page) {
    setLoading(true)
    try {
      const response = await usersApi.list({ page: nextPage, limit: 10 })
      setUsers(response.data?.users ?? [])
      setPagination(response.pagination ?? { total: 0 })
      setPage(nextPage)
    } catch (error) {
      onError(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadUsers(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <section className="space-y-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Users</h2>
        <ActionButton disabled={loading} onClick={() => loadUsers(page)} tone="gray">
          Refresh
        </ActionButton>
      </div>

      <UserCreateForm onCreated={() => loadUsers(1)} onError={onError} />

      <DataTable
        columns={[
          { key: 'id', label: 'ID' },
          { key: 'first_name', label: 'First name' },
          { key: 'last_name', label: 'Last name' },
          { key: 'email', label: 'Email' },
          { key: 'phone', label: 'Phone' },
          { key: 'gender', label: 'Gender' },
          { key: 'role', label: 'Role' },
        ]}
        emptyLabel={loading ? 'Loading...' : 'No users found'}
        pagination={{
          limit: 10,
          onPageChange: loadUsers,
          page,
          total: pagination.total ?? 0,
        }}
        rows={users}
      />
    </section>
  )
}
