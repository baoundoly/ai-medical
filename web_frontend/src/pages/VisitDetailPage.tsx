import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle, BrainCircuit } from 'lucide-react'
import api from '../lib/api'
import type { Visit, Prescription } from '../lib/types'
import { useAuth } from '../contexts/AuthContext'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import { format } from 'date-fns'

export default function VisitDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [visit, setVisit] = useState<Visit | null>(null)
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([])
  const [loading, setLoading] = useState(true)
  const [approving, setApproving] = useState(false)
  const [approveError, setApproveError] = useState('')

  useEffect(() => {
    if (!id) return
    Promise.all([
      api.get<Visit>(`/visits/${id}`),
      api.get(`/prescriptions?visitId=${id}`),
    ])
      .then(([visitRes, prescRes]) => {
        setVisit(visitRes.data)
        const d = prescRes.data
        setPrescriptions(Array.isArray(d) ? d : (d?.items ?? []))
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  const handleApprove = async () => {
    if (!id) return
    setApproveError('')
    setApproving(true)
    try {
      await api.post(`/visits/${id}/approve`)
      const res = await api.get<Visit>(`/visits/${id}`)
      setVisit(res.data)
    } catch {
      setApproveError('Failed to approve visit.')
    } finally {
      setApproving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-700" />
      </div>
    )
  }

  if (!visit) {
    return (
      <div className="text-center py-20 text-gray-500">
        Visit not found.{' '}
        <Link to="/visits" className="text-primary-600 hover:underline">
          Back to Visits
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Link to="/visits" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900">Visit Detail</h2>
          <p className="text-sm text-gray-500">{format(new Date(visit.visitDate), 'dd MMM yyyy, hh:mm a')}</p>
        </div>
        <Badge status={visit.status} />
      </div>

      {/* Visit Info */}
      <Card title="Clinical Information">
        <div className="space-y-4">
          <div>
            <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">Chief Complaint</p>
            <p className="text-gray-800 mt-1">{visit.chiefComplaint}</p>
          </div>

          {visit.aiSummary && (
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <BrainCircuit className="w-4 h-4 text-blue-600" />
                <p className="text-sm font-semibold text-blue-800">AI Clinical Summary</p>
              </div>
              <p className="text-sm text-blue-700">{visit.aiSummary}</p>
            </div>
          )}

          {visit.doctorApprovedAt && (
            <div className="flex items-center gap-2 text-green-700 text-sm">
              <CheckCircle className="w-4 h-4" />
              Approved by doctor on {format(new Date(visit.doctorApprovedAt), 'dd MMM yyyy, hh:mm a')}
            </div>
          )}
        </div>
      </Card>

      {/* Approve button */}
      {user?.role === 'Doctor' && visit.status === 'pending' && (
        <div className="flex items-center gap-3">
          <Button onClick={handleApprove} loading={approving}>
            <CheckCircle className="w-4 h-4" />
            Approve Visit
          </Button>
          {approveError && <p className="text-sm text-red-600">{approveError}</p>}
        </div>
      )}

      {/* Prescriptions */}
      <Card title="Prescriptions">
        {prescriptions.length === 0 ? (
          <p className="text-gray-400 text-sm">No prescriptions for this visit.</p>
        ) : (
          <div className="space-y-3">
            {prescriptions.map((p) => (
              <div key={p.id} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-center justify-between mb-3">
                  <p className="font-medium text-gray-800">Prescription #{p.id.slice(0, 8)}</p>
                  <Badge status={p.status} />
                </div>
                {p.items?.length > 0 && (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs text-gray-400">
                        <th className="pb-2">Medicine</th>
                        <th className="pb-2">Dosage</th>
                        <th className="pb-2">Frequency</th>
                        <th className="pb-2">Duration</th>
                        <th className="pb-2">Meal</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {p.items.map((item) => (
                        <tr key={item.id}>
                          <td className="py-1.5 font-medium text-gray-800">{item.medicineName}</td>
                          <td className="py-1.5 text-gray-600">{item.dosage}</td>
                          <td className="py-1.5 text-gray-600">{item.frequency}</td>
                          <td className="py-1.5 text-gray-600">{item.duration}</td>
                          <td className="py-1.5 text-gray-600">{item.mealInstruction}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
