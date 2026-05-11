import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Plus, X } from 'lucide-react'
import { useForm } from 'react-hook-form'
import api from '../lib/api'
import type { Visit } from '../lib/types'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Input from '../components/ui/Input'
import { format } from 'date-fns'

type StatusFilter = 'all' | 'pending' | 'completed' | 'approved'

interface NewVisitForm {
  patientId: string
  chiefComplaint: string
}

export default function VisitsPage() {
  const [visits, setVisits] = useState<Visit[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [showModal, setShowModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [apiError, setApiError] = useState('')

  const { register, handleSubmit, reset, formState: { errors } } = useForm<NewVisitForm>()

  const fetchVisits = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (statusFilter !== 'all') params.status = statusFilter
      const res = await api.get('/visits', { params })
      const data = res.data
      setVisits(Array.isArray(data) ? data : (data?.items ?? []))
    } catch {
      setVisits([])
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => { fetchVisits() }, [fetchVisits])

  const onSubmit = async (data: NewVisitForm) => {
    setApiError('')
    setSubmitting(true)
    try {
      await api.post('/visits', data)
      reset()
      setShowModal(false)
      fetchVisits()
    } catch {
      setApiError('Failed to create visit.')
    } finally {
      setSubmitting(false)
    }
  }

  const filterButtons: StatusFilter[] = ['all', 'pending', 'approved', 'completed']

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Visits</h2>
          <p className="text-sm text-gray-500 mt-0.5">{visits.length} visits</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4" />
          New Visit
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {filterButtons.map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors capitalize ${
              statusFilter === s
                ? 'bg-primary-700 text-white border-primary-700'
                : 'bg-white text-gray-600 border-gray-300 hover:border-primary-400'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      <Card>
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : visits.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No visits found.</div>
        ) : (
          <div className="space-y-3">
            {visits.map((v) => (
              <div
                key={v.id}
                className="flex items-start justify-between p-4 bg-gray-50 rounded-lg border border-gray-100 hover:border-primary-200 transition-colors"
              >
                <div className="space-y-1">
                  <p className="font-medium text-gray-900">{v.chiefComplaint}</p>
                  <p className="text-sm text-gray-500">
                    {format(new Date(v.visitDate), 'dd MMM yyyy, hh:mm a')}
                  </p>
                  {v.aiSummary && (
                    <p className="text-sm text-gray-600 italic line-clamp-1">{v.aiSummary}</p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-2 ml-4 shrink-0">
                  <Badge status={v.status} />
                  <Link to={`/visits/${v.id}`} className="text-xs text-primary-600 hover:underline">
                    View detail →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* New Visit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 className="text-lg font-semibold">New Visit</h3>
              <button onClick={() => { setShowModal(false); reset() }} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-5 space-y-4">
              {apiError && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{apiError}</p>}
              <Input
                label="Patient ID"
                placeholder="Patient UUID"
                error={errors.patientId?.message}
                {...register('patientId', { required: 'Patient ID is required' })}
              />
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Chief Complaint</label>
                <textarea
                  rows={3}
                  placeholder="Describe the chief complaint..."
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  {...register('chiefComplaint', { required: 'Chief complaint is required' })}
                />
                {errors.chiefComplaint && (
                  <p className="text-xs text-red-600">{errors.chiefComplaint.message}</p>
                )}
              </div>
              <div className="flex justify-end gap-3">
                <Button variant="secondary" type="button" onClick={() => { setShowModal(false); reset() }}>
                  Cancel
                </Button>
                <Button type="submit" loading={submitting}>
                  Create Visit
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
