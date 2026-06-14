import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { ActionButton } from '../../components/ui/ActionButton'
import { TextInput } from '../../components/ui/Inputs'
import { loginUser, selectAuth } from './authSlice'

const loginInitialState = {
  email: '',
  password: '',
}

export function LoginForm({ onSwitch }) {
  const dispatch = useDispatch()
  const { status } = useSelector(selectAuth)
  const [form, setForm] = useState(loginInitialState)

  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    })
  }

  function handleSubmit(event) {
    event.preventDefault()
    dispatch(loginUser(form))
  }

  return (
    <form className="space-y-4 text-center" onSubmit={handleSubmit}>
      <h2 className="text-xl font-bold">Login</h2>

      <TextInput
        label="Email"
        name="email"
        onChange={handleChange}
        type="email"
        value={form.email}
      />

      <TextInput
        label="Password"
        name="password"
        onChange={handleChange}
        type="password"
        value={form.password}
      />

      <div className="flex items-center justify-center gap-3">
        <ActionButton disabled={status === 'loading'} type="submit">
          {status === 'loading' ? 'Loading...' : 'Login'}
        </ActionButton>

        <button className="text-sm text-blue-400 underline" onClick={onSwitch} type="button">
          Register
        </button>
      </div>
    </form>
  )
}
