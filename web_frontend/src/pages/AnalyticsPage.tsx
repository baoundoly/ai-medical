import { useEffect, useState } from 'react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import api from '../lib/api'
import Card from '../components/ui/Card'

interface DiseaseDataPoint {
  month: string
  [disease: string]: string | number
}

interface PrescriptionDataPoint {
  doctor: string
  prescriptions: number
}

interface DoctorPerformance {
  doctorId: string
  doctorName: string
  totalVisits: number
  totalPrescriptions: number
  approvalRate: number
}

const DISEASE_COLORS = ['#1d4ed8', '#16a34a', '#dc2626', '#9333ea', '#f59e0b']

export default function AnalyticsPage() {
  const [diseaseTrend, setDiseaseTrend] = useState<DiseaseDataPoint[]>([])
  const [prescriptionData, setPrescriptionData] = useState<PrescriptionDataPoint[]>([])
  const [doctorPerf, setDoctorPerf] = useState<DoctorPerformance[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      api.get('/analytics/disease-trends'),
      api.get('/analytics/prescription-stats'),
      api.get('/analytics/doctor-performance'),
    ]).then(([diseaseRes, prescRes, perfRes]) => {
      if (diseaseRes.status === 'fulfilled') {
        setDiseaseTrend(diseaseRes.value.data ?? [])
      }
      if (prescRes.status === 'fulfilled') {
        setPrescriptionData(prescRes.value.data ?? [])
      }
      if (perfRes.status === 'fulfilled') {
        setDoctorPerf(perfRes.value.data ?? [])
      }
    }).finally(() => setLoading(false))
  }, [])

  // Derive disease keys for the line chart
  const diseaseKeys =
    diseaseTrend.length > 0
      ? Object.keys(diseaseTrend[0]).filter((k) => k !== 'month')
      : []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
        <p className="text-sm text-gray-500 mt-0.5">Clinical insights and performance metrics</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-72 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <>
          {/* Disease Trend */}
          <Card title="Disease Trend (Monthly)">
            {diseaseTrend.length === 0 ? (
              <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
                No disease trend data available.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={diseaseTrend} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  {diseaseKeys.map((key, idx) => (
                    <Line
                      key={key}
                      type="monotone"
                      dataKey={key}
                      stroke={DISEASE_COLORS[idx % DISEASE_COLORS.length]}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}
          </Card>

          {/* Prescription Analytics */}
          <Card title="Prescriptions by Doctor">
            {prescriptionData.length === 0 ? (
              <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
                No prescription data available.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={prescriptionData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="doctor" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="prescriptions" fill="#1d4ed8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>

          {/* Doctor Performance Table */}
          <Card title="Doctor Performance">
            {doctorPerf.length === 0 ? (
              <div className="text-center py-10 text-gray-400 text-sm">
                No performance data available.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm divide-y divide-gray-100">
                  <thead>
                    <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      <th className="pb-3 pr-6">Doctor</th>
                      <th className="pb-3 pr-6">Total Visits</th>
                      <th className="pb-3 pr-6">Prescriptions</th>
                      <th className="pb-3">Approval Rate</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {doctorPerf.map((d) => (
                      <tr key={d.doctorId} className="hover:bg-gray-50">
                        <td className="py-3 pr-6 font-medium text-gray-800">{d.doctorName}</td>
                        <td className="py-3 pr-6 text-gray-600">{d.totalVisits}</td>
                        <td className="py-3 pr-6 text-gray-600">{d.totalPrescriptions}</td>
                        <td className="py-3">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-100 rounded-full h-1.5 max-w-20">
                              <div
                                className="bg-primary-600 h-1.5 rounded-full"
                                style={{ width: `${Math.min(d.approvalRate, 100)}%` }}
                              />
                            </div>
                            <span className="text-gray-700 text-xs">
                              {d.approvalRate?.toFixed(1)}%
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
