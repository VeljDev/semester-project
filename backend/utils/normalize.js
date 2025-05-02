export function normalizeString(str = '') {
  return str
    .toLowerCase()
    .replace(/\s+/g, '_')        
    .replace(/[^a-z0-9-_]/g, '')
}

export function normalizeVersion(version = '') {
  return version.replace(/[()]/g, '\\$&')
}
