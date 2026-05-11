import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, CalendarDays, ClipboardList, AlertTriangle, TrendingUp } from 'lucide-react'
import api from '../lib/api'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import type { Appointment } from '../lib/types'
import { format } from 'date-fns'

interface Stats {
  totalPatients: number
  todayAppointments: number
  pendingVisits: number
  criticalLabs: number
}

interface StatCardProps {
  label: string
  value: number | string
  icon: React.ReactNode
  color: string
  loading: boolean
}

function StatCard({ label, value, icon, color, loading }: StatCardProps) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex items-center gap-4`}>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        {loading ? (
          <div className="h-7 w-16 bg-gray-100 rounded animate-pulse mt-1" />
        ) : (
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        )}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>({
    totalPatients: 0,
    todayAppointments: 0,
    pendingVisits: 0,
    criticalLabs: 0,
  })
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loadingStats, setLoadingStats] = useState(true)
  const [loadingAppts, setLoadingAppts] = useState(true)

  useEffect(() => {
    const today = format(new Date(), 'yyyy-MM-dd')

    Promise.allSettled([
      api.get('/patients?pageSize=1'),
      api.get(`/appointments?date=${today}&pageSize=1`),
      api.get('/visits?status=pending&pageSize=1'),
      api.get('/lab-reports?critical=true&pageSize=1'),
    ]).then(([patients, appts, visits, labs]) => {
      setStats({
        totalPatients:
          patients.status === 'fulfilled'
            ? (patients.value.data?.total ?? patients.value.data?.length ?? 0)
            : 0,
        todayAppointments:
          appts.status === 'fulfilled'
            ? (appts.value.data?.total ?? appts.value.data?.length ?? 0)
            : 0,
        pendingVisits:
          visits.status === 'fulfilled'
            ? (visits.value.data?.total ?? visits.value.data?.length ?? 0)
            : 0,
        criticalLabs:
          labs.status === 'fulfilled'
            ? (labs.value.data?.total ?? labs.value.data?.length ?? 0)
            : 0,
      })
      setLoadingStats(false)
    })

    api
      .get<Appointment[]>(`/appointments?date=${today}&pageSize=10`)
      .then((res) => {
        const data = res.data
        setAppointments(Array.isArray(data) ? data : (data as { items?: Appointment[] }).items ?? [])
      })
      .catch(() => setAppointments([]))
      .finally(() => setLoadingAppts(false))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-sm text-gray-500 mt-1">
          {format(new Date(), "EEEE, MMMM d, yyyy")}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Total Patients"
          value={stats.totalPatients}
          icon={<Users className="w-6 h-6 text-blue-700" />}
          color="bg-blue-50"
          loading={loadingStats}
        />
        <StatCard
          label="Today's Appointments"
          value={stats.todayAppointments}
          icon={<CalendarDays className="w-6 h-6 text-green-700" />}
          color="bg-green-50"
          loading={loadingStats}
        />
        <StatCard
          label="Pending Visits"
          value={stats.pendingVisits}
          icon={<ClipboardList className="w-6 h-6 text-yellow-700" />}
          color="bg-yellow-50"
          loading={loadingStats}
        />
        <StatCard
          label="Critical Lab Alerts"
          value={stats.criticalLabs}
          icon={<AlertTriangle className="w-6 h-6 text-red-700" />}
          color="bg-red-50"
          loading={loadingStats}
        />
      </div>

      {/* Recent Appointments */}
      <Card
        title="Today's Appointments"
        action={
          <Link to="/appointments" className="text-sm text-primary-600 hover:underline">
            View all
          </Link>
        }
      >
        {loadingAppts ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        ) : appointments.length === 0 ? (
          <div className="flex flex-col items-center py-10 text-gray-400 gap-2">
            <TrendingUp className="w-8 h-8" />
            <p className="text-sm">No appointments scheduled for today.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm divide-y divide-gray-100">
              <thead>
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  <th className="pb-3 pr-4">Token</th>
                  <th className="pb-3 pr-4">Patient ID</th>
                  <th className="pb-3 pr-4">Type</th>
                  <th className="pb-3 pr-4">Time</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {appointments.map((appt) => (
                  <tr key={appt.id} className="hover:bg-gray-50">
                    <td className="py-2.5 pr-4 font-bold text-primary-700">#{appt.tokenNumber}</td>
                    <td className="py-2.5 pr-4 text-gray-600 font-mono text-xs">{appt.patientId}</td>
                    <td className="py-2.5 pr-4 text-gray-700 capitalize">{appt.appointmentType}</td>
                    <td className="py-2.5 pr-4 text-gray-600">
                      {format(new Date(appt.scheduledAt), 'hh:mm a')}
                    </td>
                    <td className="py-2.5">
                      <div className="flex items-center gap-1.5">
                        <Badge status={appt.status} />
                        {appt.isEmergency && (
                          <Badge status="emergency" label="Emergency" />
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
