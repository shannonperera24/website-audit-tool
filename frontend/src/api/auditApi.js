import axios from 'axios'

export const runAudit = (url) =>
  axios.post('/api/audit/', { url }).then((res) => res.data)

export const getAudits = () =>
  axios.get('/api/audits/').then((res) => res.data)

export const getAudit = (id) =>
  axios.get(`/api/audits/${id}/`).then((res) => res.data)
