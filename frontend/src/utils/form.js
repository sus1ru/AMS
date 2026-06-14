export function cleanPayload(payload) {
  return Object.fromEntries(
    Object.entries(payload).map(([key, value]) => [key, value === '' ? null : value]),
  )
}

export function toIntegerOrNull(value) {
  if (value === '' || value === null || value === undefined) {
    return null
  }

  return Number(value)
}
