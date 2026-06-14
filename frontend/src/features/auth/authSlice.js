import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { authApi } from '../../lib/api'

export const checkSession = createAsyncThunk('auth/checkSession', async () => {
  return authApi.currentUser()
})

export const loginUser = createAsyncThunk('auth/loginUser', async (credentials) => {
  await authApi.login(credentials)
  return authApi.currentUser()
})

export const registerUser = createAsyncThunk('auth/registerUser', async (payload) => {
  return authApi.register(payload)
})

export const logoutUser = createAsyncThunk('auth/logoutUser', async () => {
  return authApi.logout()
})

const initialState = {
  bootstrapped: false,
  error: '',
  isAuthenticated: false,
  status: 'idle',
  user: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError(state) {
      state.error = ''
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(checkSession.pending, (state) => {
        state.status = 'loading'
      })
      .addCase(checkSession.fulfilled, (state, action) => {
        state.bootstrapped = true
        state.error = ''
        state.isAuthenticated = true
        state.status = 'idle'
        state.user = action.payload.data?.user ?? null
      })
      .addCase(checkSession.rejected, (state) => {
        state.bootstrapped = true
        state.isAuthenticated = false
        state.status = 'idle'
        state.user = null
      })
      .addCase(loginUser.pending, (state) => {
        state.error = ''
        state.status = 'loading'
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.error = ''
        state.isAuthenticated = true
        state.status = 'idle'
        state.user = action.payload.data?.user ?? null
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.error = action.error.message
        state.isAuthenticated = false
        state.status = 'idle'
        state.user = null
      })
      .addCase(registerUser.pending, (state) => {
        state.error = ''
        state.status = 'loading'
      })
      .addCase(registerUser.fulfilled, (state) => {
        state.error = ''
        state.status = 'idle'
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.error = action.error.message
        state.status = 'idle'
      })
      .addCase(logoutUser.pending, (state) => {
        state.error = ''
        state.status = 'loading'
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.error = ''
        state.isAuthenticated = false
        state.status = 'idle'
        state.user = null
      })
      .addCase(logoutUser.rejected, (state, action) => {
        state.error = action.error.message
        state.status = 'idle'
      })
  },
})

export const { clearError } = authSlice.actions

export const selectAuth = (state) => state.auth

export default authSlice.reducer
