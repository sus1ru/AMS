import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { ActionButton } from '../../components/ui/ActionButton'
import { SelectInput, TextInput } from '../../components/ui/Inputs'
import { genders, roles } from '../../constants/options'
import { cleanPayload } from '../../utils/form'
import { registerUser, selectAuth } from './authSlice'

const registerInitialState = {
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  role: 'super_admin',
  phone: '',
  dob: '',
  gender: '',
  address: '',
}

export function RegisterForm({ onSwitch }) {
  const dispatch = useDispatch()
  const { status } = useSelector(selectAuth)
  const [form, setForm] = useState(registerInitialState)

  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const result = await dispatch(registerUser(cleanPayload(form)))

    if (registerUser.fulfilled.match(result)) {
      setForm(registerInitialState)
      onSwitch()
    }
  }

  return (
    <form className="space-y-4 text-center" onSubmit={handleSubmit}>
      <h2 className="text-xl font-bold">Register</h2>

      <div className="grid gap-3 sm:grid-cols-2">
        <TextInput
          label="First name"
          name="first_name"
          onChange={handleChange}
          value={form.first_name}
        />

        <TextInput
          label="Last name"
          name="last_name"
          onChange={handleChange}
          value={form.last_name}
        />

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

        <SelectInput label="Role" name="role" onChange={handleChange} value={form.role}>
          {roles.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </SelectInput>

        <TextInput
          label="Phone"
          name="phone"
          onChange={handleChange}
          required={false}
          value={form.phone}
        />

        <TextInput
          label="DOB"
          name="dob"
          onChange={handleChange}
          required={false}
          type="date"
          value={form.dob}
        />

        <SelectInput
          label="Gender"
          name="gender"
          onChange={handleChange}
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
      </div>

      <TextInput
        label="Address"
        name="address"
        onChange={handleChange}
        required={false}
        value={form.address}
      />

      <div className="flex items-center justify-center gap-3">
        <ActionButton disabled={status === 'loading'} type="submit">
          {status === 'loading' ? 'Loading...' : 'Register'}
        </ActionButton>

        <button className="text-sm text-blue-400 underline" onClick={onSwitch} type="button">
          Back to login
        </button>
      </div>
    </form>
  )
}
