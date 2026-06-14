import { useEffect, useMemo, useState } from 'react'
import { ActionButton } from '../../components/ui/ActionButton'
import { DataTable } from '../../components/ui/DataTable'
import { SelectInput, TextInput } from '../../components/ui/Inputs'
import { Modal } from '../../components/ui/Modal'
import { genders } from '../../constants/options'
import { artistsApi } from '../../lib/api'
import { cleanPayload, toIntegerOrNull } from '../../utils/form'

const artistInitialState = {
  id: '',
  user_id: '',
  user_fullname: '',
  user_email: '',
  name: '',
  dob: '',
  gender: '',
  address: '',
  first_release_year: '',
  no_of_albums_released: '',
}

function formatUser(user) {
  if (!user) {
    return ''
  }

  const name = user.fullname || user.user_fullname || 'Current linked user'
  const email = user.email || user.user_email
  return email ? `${name} · ${email}` : name
}

function ArtistUserSearch({ form, onSearch, onSelect, options }) {
  const selectedLabel = formatUser(form)
  const [query, setQuery] = useState(selectedLabel)
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="relative text-left">
      <label className="mb-1 block text-sm text-gray-300">Artist user</label>
      <input
        autoComplete="off"
        className="w-full border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-blue-500"
        name="artist_user_search"
        onChange={(event) => {
          setQuery(event.target.value)
          setIsOpen(true)
          onSearch(event.target.value)
          onSelect({ email: '', fullname: '', id: '' })
        }}
        onFocus={() => {
          setIsOpen(true)
          onSearch(query)
        }}
        placeholder="Type a user name or email"
        value={query}
      />

      {isOpen && (
        <div className="absolute z-20 mt-1 max-h-56 w-full overflow-y-auto border border-gray-700 bg-gray-950 shadow-xl">
          <button
            className="block w-full px-3 py-2 text-left text-sm text-gray-200 hover:bg-gray-800"
            onMouseDown={(event) => {
              event.preventDefault()
              onSelect({ email: '', fullname: '', id: '' })
              setQuery('')
              setIsOpen(false)
            }}
            type="button"
          >
            No linked user
          </button>

          {options.map((user) => (
            <button
              className="block w-full px-3 py-2 text-left text-sm text-white hover:bg-gray-800"
              key={user.id}
              onMouseDown={(event) => {
                event.preventDefault()
                onSelect(user)
                setQuery(formatUser(user))
                setIsOpen(false)
              }}
              type="button"
            >
              <span className="block font-medium">{user.fullname}</span>
              <span className="block text-xs text-gray-400">{user.email}</span>
            </button>
          ))}

          {options.length === 0 && (
            <div className="px-3 py-2 text-sm text-gray-500">No available users found</div>
          )}
        </div>
      )}
    </div>
  )
}

function ArtistForm({ availableUsers, form, loading, onCancel, onChange, onSearchUsers, onSelectUser, onSubmit }) {
  const userOptions = useMemo(() => {
    const currentUser =
      form.user_id && form.user_fullname
        ? [{ email: form.user_email, fullname: form.user_fullname, id: form.user_id }]
        : []
    const ids = new Set(currentUser.map((user) => String(user.id)))
    const freshUsers = availableUsers.filter((user) => !ids.has(String(user.id)))
    return [...currentUser, ...freshUsers]
  }, [availableUsers, form.user_email, form.user_fullname, form.user_id])

  return (
    <form
      className="grid gap-4"
      onSubmit={(event) => {
        event.preventDefault()
        onSubmit()
      }}
    >
      <div className="grid gap-3 md:grid-cols-3">
        <ArtistUserSearch
          form={form}
          onSearch={onSearchUsers}
          onSelect={onSelectUser}
          options={userOptions}
        />
        <TextInput label="Name" name="name" onChange={onChange} value={form.name} />
        <TextInput
          label="DOB"
          name="dob"
          onChange={onChange}
          required={false}
          type="date"
          value={form.dob}
        />
        <SelectInput
          label="Gender"
          name="gender"
          onChange={onChange}
          required={false}
          value={form.gender}
        >
          <option value="">Select</option>
          {genders.map((gender) => (
            <option key={gender.value} value={gender.value}>
              {gender.label}
            </option>
          ))}
        </SelectInput>
        <TextInput
          label="Address"
          name="address"
          onChange={onChange}
          required={false}
          value={form.address}
        />
        <TextInput
          label="First release year"
          name="first_release_year"
          onChange={onChange}
          required={false}
          type="number"
          value={form.first_release_year}
        />
        <TextInput
          label="Albums released"
          name="no_of_albums_released"
          onChange={onChange}
          required={false}
          type="number"
          value={form.no_of_albums_released}
        />
      </div>

      <div className="flex flex-wrap gap-2">
        <ActionButton disabled={loading} type="submit">
          Save
        </ActionButton>
        <ActionButton disabled={loading} onClick={onCancel} tone="gray">
          Cancel
        </ActionButton>
      </div>
    </form>
  )
}

export function ArtistsPanel({ onError, onViewSongs, userRole }) {
  const canWriteArtists = userRole === 'artist_manager'
  const [artists, setArtists] = useState([])
  const [availableUsers, setAvailableUsers] = useState([])
  const [createForm, setCreateForm] = useState(artistInitialState)
  const [editForm, setEditForm] = useState(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  function handleCreateChange(event) {
    setCreateForm({
      ...createForm,
      [event.target.name]: event.target.value,
    })
  }

  function handleEditChange(event) {
    setEditForm({
      ...editForm,
      [event.target.name]: event.target.value,
    })
  }

  function selectCreateUser(selectedUser) {
    setCreateForm({
      ...createForm,
      user_email: selectedUser.email ?? '',
      user_fullname: selectedUser.fullname ?? '',
      user_id: selectedUser.id ? String(selectedUser.id) : '',
    })
  }

  function selectEditUser(selectedUser) {
    setEditForm({
      ...editForm,
      user_email: selectedUser.email ?? '',
      user_fullname: selectedUser.fullname ?? '',
      user_id: selectedUser.id ? String(selectedUser.id) : '',
    })
  }

  async function loadArtists() {
    setLoading(true)
    try {
      const response = await artistsApi.list({ page: 1, limit: 10 })
      setArtists(response.data?.artists ?? response.data?.users ?? [])
    } catch (error) {
      onError(error.message)
    } finally {
      setLoading(false)
    }
  }

  async function loadAvailableUsers(search = '') {
    if (!canWriteArtists) {
      return
    }

    try {
      const response = await artistsApi.availableUsers({ q: search })
      setAvailableUsers(response.data?.users ?? [])
    } catch (error) {
      onError(error.message)
    }
  }

  async function handleCreate() {
    setLoading(true)
    try {
      await artistsApi.create({
        ...cleanPayload(createForm),
        id: undefined,
        user_id: toIntegerOrNull(createForm.user_id),
        first_release_year: toIntegerOrNull(createForm.first_release_year),
        no_of_albums_released: toIntegerOrNull(createForm.no_of_albums_released),
      })
      setCreateForm(artistInitialState)
      setIsCreateOpen(false)
      await loadArtists()
    } catch (error) {
      onError(error.message)
      setLoading(false)
    }
  }

  async function handleUpdate() {
    if (!editForm) {
      return
    }

    setLoading(true)
    try {
      await artistsApi.update({
        ...cleanPayload(editForm),
        id: toIntegerOrNull(editForm.id),
        user_id: toIntegerOrNull(editForm.user_id),
        first_release_year: toIntegerOrNull(editForm.first_release_year),
        no_of_albums_released: toIntegerOrNull(editForm.no_of_albums_released),
      })
      setEditForm(null)
      await loadArtists()
    } catch (error) {
      onError(error.message)
      setLoading(false)
    }
  }

  async function handleDelete(artistId) {
    setLoading(true)
    try {
      await artistsApi.remove(toIntegerOrNull(artistId))
      if (editForm?.id === String(artistId)) {
        setEditForm(null)
      }
      await loadArtists()
    } catch (error) {
      onError(error.message)
      setLoading(false)
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadArtists()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (canWriteArtists) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      loadAvailableUsers()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canWriteArtists])

  return (
    <section className="space-y-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Artists</h2>
        <div className="flex gap-2">
          {canWriteArtists && (
            <ActionButton
              disabled={loading}
              onClick={() => {
                setCreateForm(artistInitialState)
                setIsCreateOpen(true)
                loadAvailableUsers()
              }}
            >
              Create artist
            </ActionButton>
          )}
          <ActionButton disabled={loading} onClick={loadArtists} tone="gray">
            Refresh
          </ActionButton>
        </div>
      </div>

      {canWriteArtists && isCreateOpen && (
        <Modal onClose={() => setIsCreateOpen(false)} title="Create artist">
          <ArtistForm
            availableUsers={availableUsers}
            form={createForm}
            loading={loading}
            onCancel={() => setIsCreateOpen(false)}
            onChange={handleCreateChange}
            onSearchUsers={loadAvailableUsers}
            onSelectUser={selectCreateUser}
            onSubmit={handleCreate}
          />
        </Modal>
      )}

      {canWriteArtists && editForm && (
        <Modal onClose={() => setEditForm(null)} title="Update artist">
          <ArtistForm
            availableUsers={availableUsers}
            form={editForm}
            loading={loading}
            onCancel={() => setEditForm(null)}
            onChange={handleEditChange}
            onSearchUsers={loadAvailableUsers}
            onSelectUser={selectEditUser}
            onSubmit={handleUpdate}
          />
        </Modal>
      )}

      <DataTable
        columns={[
          { key: 'id', label: 'ID' },
          {
            key: 'user_fullname',
            label: 'Artist user',
            render: (artist) =>
              artist.user_fullname
                ? `${artist.user_fullname}${artist.user_email ? ` · ${artist.user_email}` : ''}`
                : '-',
          },
          { key: 'name', label: 'Name' },
          { key: 'gender', label: 'Gender' },
          { key: 'first_release_year', label: 'First release' },
          { key: 'no_of_albums_released', label: 'Albums' },
          { key: 'address', label: 'Address' },
          {
            key: 'actions',
            label: 'Action',
            render: (artist) =>
              canWriteArtists ? (
                <div className="flex gap-3">
                  <button
                    className="text-blue-400 underline"
                    onClick={() => onViewSongs(artist.id)}
                    type="button"
                  >
                    Songs
                  </button>
                  <button
                    className="text-blue-400 underline"
                    onClick={() => {
                      setEditForm({
                        id: String(artist.id ?? ''),
                        user_id: artist.user_id ? String(artist.user_id) : '',
                        user_fullname: artist.user_fullname ?? '',
                        user_email: artist.user_email ?? '',
                        name: artist.name ?? '',
                        dob: artist.dob?.slice(0, 10) ?? '',
                        gender: artist.gender ?? '',
                        address: artist.address ?? '',
                        first_release_year: artist.first_release_year
                          ? String(artist.first_release_year)
                          : '',
                        no_of_albums_released: artist.no_of_albums_released
                          ? String(artist.no_of_albums_released)
                          : '',
                      })
                      loadAvailableUsers()
                    }}
                    type="button"
                  >
                    Edit
                  </button>
                  <button
                    className="text-red-400 underline"
                    onClick={() => handleDelete(artist.id)}
                    type="button"
                  >
                    Delete
                  </button>
                </div>
              ) : (
                <button
                  className="text-blue-400 underline"
                  onClick={() => onViewSongs(artist.id)}
                  type="button"
                >
                  Songs
                </button>
              ),
          },
        ]}
        emptyLabel={loading ? 'Loading...' : 'No artists found'}
        rows={artists}
      />
    </section>
  )
}
