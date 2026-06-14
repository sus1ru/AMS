import { useMemo, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { ActionButton } from '../../components/ui/ActionButton'
import { ArtistsPanel } from '../artists/ArtistsPanel'
import { logoutUser, selectAuth } from '../auth/authSlice'
import { SongsPanel } from '../songs/SongsPanel'
import { UsersPanel } from '../users/UsersPanel'

export function Dashboard() {
  const dispatch = useDispatch()
  const { status, user } = useSelector(selectAuth)
  const [selectedTab, setSelectedTab] = useState('')
  const [selectedSongArtistId, setSelectedSongArtistId] = useState('')
  const [localError, setLocalError] = useState('')

  const tabs = useMemo(() => {
    if (!user) {
      return []
    }

    const visibleTabs = []

    if (user.role === 'super_admin') {
      visibleTabs.push({ key: 'users', label: 'Users' })
    }

    if (user.role === 'super_admin' || user.role === 'artist_manager') {
      visibleTabs.push({ key: 'artists', label: 'Artists' })
    }

    visibleTabs.push({ key: 'songs', label: 'Songs' })

    return visibleTabs
  }, [user])

  const activeTab = tabs.some((tab) => tab.key === selectedTab)
    ? selectedTab
    : (tabs[0]?.key ?? '')

  function handleTabChange(tab) {
    setLocalError('')
    setSelectedTab(tab)
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800 pb-4">
        <div className="text-left">
          <h1 className="text-2xl font-bold">AMS Admin</h1>
          <p className="mt-1 text-sm text-gray-400">
            {user?.email} · {user?.role}
          </p>
        </div>

        <ActionButton
          disabled={status === 'loading'}
          onClick={() => dispatch(logoutUser())}
          tone="red"
        >
          {status === 'loading' ? 'Logging out...' : 'Logout'}
        </ActionButton>
      </div>

      {localError && (
        <div className="border border-red-700 bg-red-950 p-3 text-sm text-red-200">
          {localError}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            className={`border px-4 py-2 text-sm font-medium ${
              activeTab === tab.key
                ? 'border-blue-500 bg-blue-600 text-white'
                : 'border-gray-700 bg-gray-900 text-gray-300 hover:bg-gray-800'
            }`}
            key={tab.key}
            onClick={() => handleTabChange(tab.key)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'users' && <UsersPanel onError={setLocalError} />}
      {activeTab === 'artists' && (
        <ArtistsPanel
          onError={setLocalError}
          onViewSongs={(artistId) => {
            setSelectedSongArtistId(String(artistId))
            setSelectedTab('songs')
          }}
          userRole={user?.role}
        />
      )}
      {activeTab === 'songs' && (
        <SongsPanel
          initialArtistId={selectedSongArtistId}
          onError={setLocalError}
          user={user}
          userRole={user?.role}
        />
      )}
    </div>
  )
}
