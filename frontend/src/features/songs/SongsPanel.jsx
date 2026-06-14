import { useEffect, useMemo, useState } from 'react'
import { ActionButton } from '../../components/ui/ActionButton'
import { DataTable } from '../../components/ui/DataTable'
import { SelectInput, TextInput } from '../../components/ui/Inputs'
import { Modal } from '../../components/ui/Modal'
import { genres } from '../../constants/options'
import { songsApi } from '../../lib/api'
import { cleanPayload, toIntegerOrNull } from '../../utils/form'

const songInitialState = {
  id: '',
  artist_id: '',
  title: '',
  album_name: '',
  genre: 'rock',
}

function ArtistAutocomplete({ onSearch, onSelect, options, selectedArtist }) {
  const [query, setQuery] = useState(selectedArtist?.name ?? '')
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    if (selectedArtist) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setQuery(selectedArtist.name)
    }
  }, [selectedArtist])

  return (
    <div className="relative min-w-64 text-left">
      <label className="mb-1 block text-sm text-gray-300">Filter artist</label>
      <input
        autoComplete="off"
        className="w-full border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-blue-500"
        name="artist_filter"
        onChange={(event) => {
          const nextQuery = event.target.value
          setQuery(nextQuery)
          setIsOpen(true)
          onSearch(nextQuery)
          onSelect(null)
        }}
        onFocus={() => {
          setIsOpen(true)
          onSearch(query)
        }}
        placeholder="All artists"
        value={query}
      />

      {isOpen && (
        <div className="absolute z-20 mt-1 max-h-56 w-full overflow-y-auto border border-gray-700 bg-gray-950 shadow-xl">
          <button
            className="block w-full px-3 py-2 text-left text-sm text-gray-200 hover:bg-gray-800"
            onMouseDown={(event) => {
              event.preventDefault()
              onSelect(null)
              setQuery('')
              setIsOpen(false)
            }}
            type="button"
          >
            All artists
          </button>

          {options.map((artist) => (
            <button
              className="block w-full px-3 py-2 text-left text-sm text-white hover:bg-gray-800"
              key={artist.id}
              onMouseDown={(event) => {
                event.preventDefault()
                onSelect(artist)
                setQuery(artist.name)
                setIsOpen(false)
              }}
              type="button"
            >
              {artist.name}
            </button>
          ))}

          {options.length === 0 && (
            <div className="px-3 py-2 text-sm text-gray-500">No artists found</div>
          )}
        </div>
      )}
    </div>
  )
}

function SongForm({ artists, form, loading, onCancel, onChange, onSubmit, ownArtistId, ownArtistName }) {
  return (
    <form
      className="grid gap-4"
      onSubmit={(event) => {
        event.preventDefault()
        onSubmit()
      }}
    >
      <div className="grid gap-3 md:grid-cols-4">
        {artists.length > 0 ? (
          <SelectInput
            label="Artist"
            name="artist_id"
            onChange={onChange}
            required={false}
            value={form.artist_id}
          >
            <option value="">Use current artist</option>
            {artists.map((artist) => (
              <option key={artist.id} value={artist.id}>
                {artist.name}
              </option>
            ))}
          </SelectInput>
        ) : (
          <SelectInput
            label="Artist"
            name="artist_id"
            onChange={onChange}
            required={false}
            value={form.artist_id || ownArtistId}
          >
            <option value={ownArtistId}>{ownArtistName || 'Current artist'}</option>
          </SelectInput>
        )}
        <TextInput label="Title" name="title" onChange={onChange} value={form.title} />
        <TextInput
          label="Album"
          name="album_name"
          onChange={onChange}
          required={false}
          value={form.album_name}
        />
        <SelectInput label="Genre" name="genre" onChange={onChange} value={form.genre}>
          {genres.map((genre) => (
            <option key={genre} value={genre}>
              {genre}
            </option>
          ))}
        </SelectInput>
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

export function SongsPanel({ initialArtistId = '', onError, user, userRole }) {
  const canListArtists = userRole === 'super_admin' || userRole === 'artist_manager'
  const canWriteSongs = userRole === 'artist'
  const [artists, setArtists] = useState([])
  const [artistOptions, setArtistOptions] = useState([])
  const [artistSearch, setArtistSearch] = useState('')
  const [songs, setSongs] = useState([])
  const [createForm, setCreateForm] = useState(songInitialState)
  const [editForm, setEditForm] = useState(null)
  const [filterArtistId, setFilterArtistId] = useState(initialArtistId ? String(initialArtistId) : '')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const ownArtistId = user?.artist_id ? String(user.artist_id) : ''
  const ownArtistName = user?.artist_name || (ownArtistId ? `Artist ${ownArtistId}` : '')
  const [selectedArtistId, setSelectedArtistId] = useState(ownArtistId)
  const [loading, setLoading] = useState(false)

  const artistById = useMemo(() => {
    const rows = [...artists]
    if (ownArtistId) {
      rows.push({ id: Number(ownArtistId), name: ownArtistName })
    }

    return rows.reduce((lookup, artist) => {
      lookup[String(artist.id)] = artist.name
      return lookup
    }, {})
  }, [artists, ownArtistId, ownArtistName])

  const selectedFilterArtist = useMemo(
    () =>
      filterArtistId
        ? { id: filterArtistId, name: artistById[String(filterArtistId)] || `Artist ${filterArtistId}` }
        : null,
    [artistById, filterArtistId],
  )

  const visibleSongs = useMemo(() => {
    if (!canListArtists || !filterArtistId) {
      return songs
    }

    return songs.filter((song) => String(song.artist_id) === String(filterArtistId))
  }, [canListArtists, filterArtistId, songs])

  const groupedSongs = useMemo(() => {
    return visibleSongs.reduce((groups, song) => {
      const artistId = String(song.artist_id)
      const artistName = artistById[artistId] || `Artist ${artistId}`
      const existingGroup = groups.find((group) => group.artistId === artistId)

      if (existingGroup) {
        existingGroup.songs.push(song)
        return groups
      }

      groups.push({ artistId, artistName, songs: [song] })
      return groups
    }, [])
  }, [artistById, visibleSongs])

  function handleChange(event) {
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

  async function loadArtists(search = artistSearch) {
    if (!canListArtists) {
      if (ownArtistId) {
        setArtists([{ id: Number(ownArtistId), name: ownArtistName }])
        setArtistOptions([{ id: Number(ownArtistId), name: ownArtistName }])
      }
      return
    }

    try {
      const response = await songsApi.availableArtists({ q: search })
      const artistRows = response.data?.artists ?? []
      if (!search) {
        setArtists(artistRows)
      }
      setArtistOptions(artistRows)
    } catch (error) {
      onError(error.message)
    }
  }

  async function loadSongs() {
    setLoading(true)
    try {
      const response = await songsApi.list({ page: 1, limit: 100 })
      const firstPageSongs = response.data?.songs ?? []
      const totalSongs = response.pagination?.total ?? firstPageSongs.length

      if (totalSongs > firstPageSongs.length) {
        const fullResponse = await songsApi.list({ page: 1, limit: totalSongs })
        setSongs(fullResponse.data?.songs ?? [])
        return
      }

      setSongs(firstPageSongs)
    } catch (error) {
      onError(error.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate() {
    setLoading(true)
    try {
      await songsApi.create({
        ...cleanPayload(createForm),
        id: undefined,
        artist_id: toIntegerOrNull(createForm.artist_id || selectedArtistId),
      })
      const artistId = createForm.artist_id || selectedArtistId
      setCreateForm({ ...songInitialState, artist_id: artistId })
      setIsCreateOpen(false)
      await loadSongs()
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
      await songsApi.update({
        ...cleanPayload(editForm),
        id: toIntegerOrNull(editForm.id),
        artist_id: toIntegerOrNull(editForm.artist_id || selectedArtistId),
      })
      setEditForm(null)
      await loadSongs()
    } catch (error) {
      onError(error.message)
      setLoading(false)
    }
  }

  async function handleDelete(songId) {
    setLoading(true)
    try {
      await songsApi.remove(toIntegerOrNull(songId))
      if (editForm?.id === String(songId)) {
        setEditForm(null)
      }
      await loadSongs()
    } catch (error) {
      onError(error.message)
      setLoading(false)
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadArtists(artistSearch)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [artistSearch, canListArtists, ownArtistId, ownArtistName])

  useEffect(() => {
    if (initialArtistId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFilterArtistId(String(initialArtistId))
    }
  }, [initialArtistId])

  useEffect(() => {
    if (!canListArtists && ownArtistId && ownArtistId !== selectedArtistId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSelectedArtistId(ownArtistId)
      setCreateForm((current) => ({ ...current, artist_id: ownArtistId }))
    }
  }, [canListArtists, ownArtistId, selectedArtistId])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadSongs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canListArtists, ownArtistId])

  const songColumns = [
    { key: 'id', label: 'ID' },
    { key: 'title', label: 'Title' },
    { key: 'album_name', label: 'Album' },
    { key: 'genre', label: 'Genre' },
    {
      key: 'actions',
      label: 'Action',
      render: (song) =>
        canWriteSongs ? (
          <div className="flex gap-3">
            <button
              className="text-blue-400 underline"
              onClick={() =>
                setEditForm({
                  id: String(song.id ?? ''),
                  artist_id: String(song.artist_id ?? ''),
                  title: song.title ?? '',
                  album_name: song.album_name ?? '',
                  genre: song.genre ?? 'rock',
                })
              }
              type="button"
            >
              Edit
            </button>
            <button
              className="text-red-400 underline"
              onClick={() => handleDelete(song.id)}
              type="button"
            >
              Delete
            </button>
          </div>
        ) : (
          <span className="text-gray-500">View only</span>
        ),
    },
  ]

  const artistSongColumns = canListArtists
    ? songColumns
    : [
        {
          key: 'artist_id',
          label: 'Artist',
          render: (song) => artistById[String(song.artist_id)] ?? `Artist ${song.artist_id}`,
        },
        ...songColumns,
      ]

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h2 className="text-lg font-semibold">Songs</h2>
        <div className="flex flex-wrap items-end gap-2">
          {canListArtists ? (
            <ArtistAutocomplete
              onSearch={setArtistSearch}
              onSelect={(artist) => setFilterArtistId(artist ? String(artist.id) : '')}
              options={artistOptions}
              selectedArtist={selectedFilterArtist}
            />
          ) : (
            <div className="min-w-52 text-left">
              <label className="mb-1 block text-sm text-gray-300">Artist</label>
              <div className="border border-gray-700 bg-gray-950 px-3 py-2 text-white">
                {ownArtistName || 'No linked artist'}
              </div>
            </div>
          )}
          <ActionButton disabled={loading} onClick={loadSongs}>
            Refresh
          </ActionButton>
          {canWriteSongs && (
            <ActionButton
              disabled={loading || !selectedArtistId}
              onClick={() => {
                setCreateForm({ ...songInitialState, artist_id: selectedArtistId })
                setIsCreateOpen(true)
              }}
            >
              Create song
            </ActionButton>
          )}
        </div>
      </div>

      {canWriteSongs && isCreateOpen && (
        <Modal onClose={() => setIsCreateOpen(false)} title="Create song">
          <SongForm
            artists={artists}
            form={createForm}
            loading={loading}
            onCancel={() => setIsCreateOpen(false)}
            onChange={handleChange}
            onSubmit={handleCreate}
            ownArtistId={ownArtistId}
            ownArtistName={ownArtistName}
          />
        </Modal>
      )}

      {canWriteSongs && editForm && (
        <Modal onClose={() => setEditForm(null)} title="Update song">
          <SongForm
            artists={artists}
            form={editForm}
            loading={loading}
            onCancel={() => setEditForm(null)}
            onChange={handleEditChange}
            onSubmit={handleUpdate}
            ownArtistId={ownArtistId}
            ownArtistName={ownArtistName}
          />
        </Modal>
      )}

      {canListArtists ? (
        <div className="space-y-5">
          {groupedSongs.length === 0 ? (
            <DataTable columns={songColumns} emptyLabel={loading ? 'Loading...' : 'No songs found'} rows={[]} />
          ) : (
            groupedSongs.map((group) => (
              <div className="space-y-2" key={group.artistId}>
                <h3 className="text-sm font-semibold text-gray-300">{group.artistName}</h3>
                <DataTable
                  columns={songColumns}
                  emptyLabel={loading ? 'Loading...' : 'No songs found'}
                  rows={group.songs}
                />
              </div>
            ))
          )}
        </div>
      ) : (
        <DataTable
          columns={artistSongColumns}
          emptyLabel={loading ? 'Loading...' : 'No songs found'}
          rows={visibleSongs}
        />
      )}
    </section>
  )
}
