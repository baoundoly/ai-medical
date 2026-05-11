import { useEffect, useState, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { Plus, X, Zap } from 'lucide-react'
import api from '../lib/api'
import type { Appointment } from '../lib/types'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Input from '../components/ui/Input'
import { format } from 'date-fns'

interface NewAppointmentForm {
  patientId: string
  scheduledAt: string
  appointmentType: string
  isEmergency: boolean
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [apiError, setApiError] = useState('')

  const { register, handleSubmit, reset, formState: { errors } } = useForm<NewAppointmentForm>({
    defaultValues: { appointmentType: 'general', isEmergency: false },
  })

  const today = format(new Date(), 'yyyy-MM-dd')

  const fetchAppointments = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get(`/appointments?date=${today}`)
      const data = res.data
      setAppointments(Array.isArray(data) ? data : (data?.items ?? []))
    } catch {
      setAppointments([])
    } finally {
      setLoading(false)
    }
  }, [today])

  useEffect(() => { fetchAppointments() }, [fetchAppointments])

  const onSubmit = async (data: NewAppointmentForm) => {
    setApiError('')
    setSubmitting(true)
    try {
      await api.post('/appointments', data)
      reset()
      setShowModal(false)
      fetchAppointments()
    } catch {
      setApiError('Failed to book appointment.')
    } finally {
      setSubmitting(false)
    }
  }

  const queue = appointments
    .filter((a) => a.status === 'scheduled' || a.status === 'pending')
    .sort((a, b) => {
      if (a.isEmergency !== b.isEmergency) return a.isEmergency ? -1 : 1
      return a.tokenNumber - b.tokenNumber
    })

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Appointments</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            {format(new Date(), 'EEEE, MMMM d, yyyy')}
          </p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4" />
          Book Appointment
        </Button>
      </div>

      {/* Today's Queue */}
      <Card title={`Today's Queue (${queue.length})`}>
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : queue.length === 0 ? (
          <p className="text-center text-gray-400 py-8">No pending appointments today.</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
            {queue.map((appt) => (
              <div
                key={appt.id}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border-2 text-center ${
                  appt.isEmergency
                    ? 'border-red-400 bg-red-50'
                    : 'border-primary-200 bg-primary-50'
                }`}
              >
                <span className={`text-2xl font-bold ${appt.isEmergency ? 'text-red-700' : 'text-primary-700'}`}>
                  #{appt.tokenNumber}
                </span>
                <span className="text-xs text-gray-500 mt-1 truncate w-full text-center">
                  {format(new Date(appt.scheduledAt), 'hh:mm a')}
                </span>
                {appt.isEmergency && (
                  <span className="flex items-center gap-0.5 text-xs text-red-600 font-semibold mt-1">
                    <Zap className="w-3 h-3" />
                    EMERGENCY
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Full Appointment List */}
      <Card title="All Appointments Today">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="h-14 bg-gray-100 rounded animate-pulse" />)}
          </div>
        ) : appointments.length === 0 ? (
          <p className="text-center text-gray-400 py-8">No appointments today.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm divide-y divide-gray-100">
              <thead>
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  <th className="pb-3 pr-4">Token</th>
                  <th className="pb-3 pr-4">Patient ID</th>
                  <th className="pb-3 pr-4">Type</th>
                  <th className="pb-3 pr-4">Time</th>
                  <th className="pb-3 pr-4">Status</th>
                  <th className="pb-3">Emergency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {appointments.map((appt) => (
                  <tr key={appt.id} className="hover:bg-gray-50">
                    <td className="py-3 pr-4 font-bold text-primary-700">#{appt.tokenNumber}</td>
                    <td className="py-3 pr-4 font-mono text-xs text-gray-500">{appt.patientId}</td>
                    <td className="py-3 pr-4 capitalize text-gray-700">{appt.appointmentType}</td>
                    <td className="py-3 pr-4 text-gray-600">
                      {format(new Date(appt.scheduledAt), 'hh:mm a')}
                    </td>
                    <td className="py-3 pr-4"><Badge status={appt.status} /></td>
                    <td className="py-3">
                      {appt.isEmergency ? (
                        <Badge status="emergency" label="Emergency" />
                      ) : (
                        <span className="text-gray-300">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Book Appointment Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 className="text-lg font-semibold">Book Appointment</h3>
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
              <Input
                label="Scheduled At"
                type="datetime-local"
                error={errors.scheduledAt?.message}
                {...register('scheduledAt', { required: 'Schedule time is required' })}
              />
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Appointment Type</label>
                <select
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  {...register('appointmentType')}
                >
                  <option value="general">General</option>
                  <option value="follow-up">Follow-up</option>
                  <option value="specialist">Specialist</option>
                  <option value="dental">Dental</option>
                </select>
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded border-gray-300 text-primary-700" {...register('isEmergency')} />
                <span className="text-sm text-gray-700 font-medium">Emergency</span>
              </label>
              <div className="flex justify-end gap-3">
                <Button variant="secondary" type="button" onClick={() => { setShowModal(false); reset() }}>
                  Cancel
                </Button>
                <Button type="submit" loading={submitting}>
                  Book Appointment
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
