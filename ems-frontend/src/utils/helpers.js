export function formatDate(iso) {
  return new Date(iso).toLocaleString()
}

export function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}
