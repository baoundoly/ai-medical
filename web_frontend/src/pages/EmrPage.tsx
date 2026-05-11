import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Stethoscope, FileText, FlaskConical, Activity, Calendar } from 'lucide-react'
import api from '../lib/api'
import type { Patient, Visit, Prescription, LabReport, VitalSigns } from '../lib/types'
import Badge from '../components/ui/Badge'
import { format } from 'date-fns'

type TimelineItem =
  | { type: 'visit'; date: string; data: Visit }
  | { type: 'prescription'; date: string; data: Prescription }
  | { type: 'lab'; date: string; data: LabReport }
  | { type: 'vitals'; date: string; data: VitalSigns & { visitDate?: string } }

const iconMap = {
  visit: <Stethoscope className="w-4 h-4 text-blue-600" />,
  prescription: <FileText className="w-4 h-4 text-green-600" />,
  lab: <FlaskConical className="w-4 h-4 text-purple-600" />,
  vitals: <Activity className="w-4 h-4 text-orange-600" />,
}

const colorMap = {
  visit: 'bg-blue-50 border-blue-200',
  prescription: 'bg-green-50 border-green-200',
  lab: 'bg-purple-50 border-purple-200',
  vitals: 'bg-orange-50 border-orange-200',
}

const dotColor = {
  visit: 'bg-blue-500',
  prescription: 'bg-green-500',
  lab: 'bg-purple-500',
  vitals: 'bg-orange-500',
}

export default function EmrPage() {
  const { patientId } = useParams<{ patientId: string }>()
  const [patient, setPatient] = useState<Patient | null>(null)
  const [timeline, setTimeline] = useState<TimelineItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!patientId) return
    Promise.allSettled([
      api.get<Patient>(`/patients/${patientId}`),
      api.get(`/visits?patientId=${patientId}`),
      api.get(`/prescriptions?patientId=${patientId}`),
      api.get(`/lab-reports?patientId=${patientId}`),
      api.get(`/vital-signs?patientId=${patientId}`),
    ]).then(([patRes, visRes, preRes, labRes, vitRes]) => {
      if (patRes.status === 'fulfilled') setPatient(patRes.value.data)

      const items: TimelineItem[] = []

      if (visRes.status === 'fulfilled') {
        const visits: Visit[] = Array.isArray(visRes.value.data)
          ? visRes.value.data
          : (visRes.value.data?.items ?? [])
        visits.forEach((v) => items.push({ type: 'visit', date: v.visitDate, data: v }))
      }

      if (preRes.status === 'fulfilled') {
        const prescriptions: Prescription[] = Array.isArray(preRes.value.data)
          ? preRes.value.data
          : (preRes.value.data?.items ?? [])
        prescriptions.forEach((p) =>
          items.push({ type: 'prescription', date: p.signedAt ?? new Date().toISOString(), data: p }),
        )
      }

      if (labRes.status === 'fulfilled') {
        const labs: LabReport[] = Array.isArray(labRes.value.data)
          ? labRes.value.data
          : (labRes.value.data?.items ?? [])
        labs.forEach((lr) => items.push({ type: 'lab', date: lr.uploadedAt, data: lr }))
      }

      if (vitRes.status === 'fulfilled') {
        const vitals: (VitalSigns & { visitDate?: string })[] = Array.isArray(vitRes.value.data)
          ? vitRes.value.data
          : (vitRes.value.data?.items ?? [])
        vitals.forEach((vs) =>
          items.push({ type: 'vitals', date: vs.visitDate ?? new Date().toISOString(), data: vs }),
        )
      }

      items.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      setTimeline(items)
    }).finally(() => setLoading(false))
  }, [patientId])

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Link
          to={patientId ? `/patients/${patientId}` : '/patients'}
          className="text-gray-400 hover:text-gray-600"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            EMR Timeline{patient ? ` — ${patient.name}` : ''}
          </h2>
          {patient && (
            <p className="text-sm text-gray-500 font-mono">{patient.patientUid}</p>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 flex-wrap">
        {(Object.entries(dotColor) as [keyof typeof dotColor, string][]).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5">
            <span className={`w-2.5 h-2.5 rounded-full ${color}`} />
            <span className="text-xs text-gray-500 capitalize">{type}</span>
          </div>
        ))}
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : timeline.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <Calendar className="w-10 h-10 mx-auto mb-2 opacity-30" />
          <p>No medical records found for this patient.</p>
        </div>
      ) : (
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-5 top-2 bottom-2 w-0.5 bg-gray-200" />
          <div className="space-y-4">
            {timeline.map((item, idx) => (
              <div key={idx} className="flex gap-4">
                {/* Dot */}
                <div className="relative z-10 flex-shrink-0 w-10 h-10 flex items-center justify-center">
                  <span className={`w-3 h-3 rounded-full border-2 border-white shadow ${dotColor[item.type]}`} />
                </div>

                {/* Card */}
                <div className={`flex-1 border rounded-xl p-4 ${colorMap[item.type]}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {iconMap[item.type]}
                      <span className="text-xs font-semibold uppercase tracking-wide text-gray-600 capitalize">
                        {item.type}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">
                      {format(new Date(item.date), 'dd MMM yyyy, hh:mm a')}
                    </span>
                  </div>

                  {item.type === 'visit' && (
                    <div>
                      <p className="font-medium text-gray-800">{item.data.chiefComplaint}</p>
                      {item.data.aiSummary && (
                        <p className="text-sm text-gray-600 italic mt-1">{item.data.aiSummary}</p>
                      )}
                      <div className="mt-2">
                        <Badge status={item.data.status} />
                      </div>
                    </div>
                  )}

                  {item.type === 'prescription' && (
                    <div>
                      <p className="font-medium text-gray-800">
                        Prescription with {item.data.items?.length ?? 0} medicine(s)
                      </p>
                      {item.data.items?.slice(0, 3).map((med) => (
                        <span key={med.id} className="inline-block text-xs bg-white border border-gray-200 rounded-full px-2 py-0.5 mr-1 mt-1">
                          {med.medicineName}
                        </span>
                      ))}
                      <div className="mt-2">
                        <Badge status={item.data.status} />
                      </div>
                    </div>
                  )}

                  {item.type === 'lab' && (
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-800">{item.data.reportType}</p>
                        {item.data.isCritical && <Badge status="critical" label="Critical" />}
                      </div>
                      {item.data.aiAnalysis && (
                        <p className="text-sm text-gray-600 italic mt-1">{item.data.aiAnalysis}</p>
                      )}
                    </div>
                  )}

                  {item.type === 'vitals' && (
                    <div className="grid grid-cols-3 sm:grid-cols-5 gap-3">
                      {[
                        { label: 'BP', value: `${item.data.bpSystolic}/${item.data.bpDiastolic}` },
                        { label: 'Pulse', value: `${item.data.pulse} bpm` },
                        { label: 'Temp', value: `${item.data.temperature}°F` },
                        { label: 'SpO2', value: `${item.data.spo2}%` },
                        { label: 'BMI', value: item.data.bmi?.toFixed(1) ?? '-' },
                      ].map(({ label, value }) => (
                        <div key={label}>
                          <p className="text-xs text-gray-400">{label}</p>
                          <p className="text-sm font-semibold text-gray-800">{value}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
