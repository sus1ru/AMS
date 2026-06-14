import { useState } from 'react'
import { ActionButton } from '../../components/ui/ActionButton'
import { SelectInput, TextInput } from '../../components/ui/Inputs'
import { genders, roles } from '../../constants/options'
import { usersApi } from '../../lib/api'
import { cleanPayload } from '../../utils/form'

const userInitialState = {
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  role: 'artist',
  phone: '',
  dob: '',
  gender: '',
  address: '',
}

export function UserCreateForm({ onCreated, onError }) {
  const [form, setForm] = useState(userInitialState)
  const [loading, setLoading] = useState(false)

  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)

    try {
      await usersApi.create(cleanPayload(form))
      setForm(userInitialState)
      await onCreated()
    } catch (error) {
      onError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="grid gap-3 border border-gray-800 bg-gray-950 p-4" onSubmit={handleSubmit}>
      <div className="grid gap-3 md:grid-cols-4">
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

      <div>
        <ActionButton disabled={loading} type="submit">
          {loading ? 'Creating...' : 'Create user'}
        </ActionButton>
      </div>
    </form>
  )
}
