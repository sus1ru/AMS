import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Dashboard } from './features/dashboard/Dashboard'
import { LoginForm } from './features/auth/LoginForm'
import { RegisterForm } from './features/auth/RegisterForm'
import { checkSession, clearError, selectAuth } from './features/auth/authSlice'

function App() {
  const dispatch = useDispatch()
  const { bootstrapped, error, isAuthenticated } = useSelector(selectAuth)
  const [page, setPage] = useState('login')

  useEffect(() => {
    dispatch(checkSession())
  }, [dispatch])

  function showLogin() {
    dispatch(clearError())
    setPage('login')
  }

  function showRegister() {
    dispatch(clearError())
    setPage('register')
  }

  if (!bootstrapped) {
    return (
      <div className="grid min-h-screen place-items-center bg-gray-950 p-6 text-white">
        Loading...
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gray-950 p-4 text-gray-100 sm:p-6">
      <div
        className={`mx-auto w-full border border-gray-800 bg-gray-900 p-5 ${
          isAuthenticated ? 'max-w-6xl' : 'max-w-xl'
        }`}
      >
        {!isAuthenticated && <h1 className="mb-6 text-center text-2xl font-bold">AMS Admin</h1>}

        {error && (
          <div className="mb-4 border border-red-700 bg-red-950 p-3 text-center text-sm text-red-200">
            {error}
          </div>
        )}

        {isAuthenticated ? (
          <Dashboard />
        ) : page === 'login' ? (
          <LoginForm onSwitch={showRegister} />
        ) : (
          <RegisterForm onSwitch={showLogin} />
        )}
      </div>
    </main>
  )
}

export default App
