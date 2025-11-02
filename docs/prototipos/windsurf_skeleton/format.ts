export const fmt = {
  number(n?: number | null, d=1) {
    if (n==null) return '-'
    return n.toLocaleString('pt-BR', { maximumFractionDigits: d })
  },
  date(s?: string) {
    if (!s) return '-'
    const dt = new Date(s)
    return dt.toLocaleDateString('pt-BR')
  }
}
