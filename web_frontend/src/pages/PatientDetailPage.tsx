import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, User, FileText, FlaskConical, Activity, ShieldAlert } from 'lucide-react'
import api from '../lib/api'
import type { Patient, Visit, Prescription, LabReport, VitalSigns } from '../lib/types'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { format } from 'date-fns'

type TabKey = 'visits' | 'prescriptions' | 'lab-reports' | 'vitals' | 'allergies'

const tabs: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: 'visits', label: 'Visits', icon: <FileText className="w-4 h-4" /> },
  { key: 'prescriptions', label: 'Prescriptions', icon: <FileText className="w-4 h-4" /> },
  { key: 'lab-reports', label: 'Lab Reports', icon: <FlaskConical className="w-4 h-4" /> },
  { key: 'vitals', label: 'Vitals', icon: <Activity className="w-4 h-4" /> },
  { key: 'allergies', label: 'Allergies', icon: <ShieldAlert className="w-4 h-4" /> },
]

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [patient, setPatient] = useState<Patient | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<TabKey>('visits')
  const [tabData, setTabData] = useState<unknown[]>([])
  const [tabLoading, setTabLoading] = useState(false)

  useEffect(() => {
    if (!id) return
    api.get<Patient>(`/patients/${id}`)
      .then((r) => setPatient(r.data))
      .catch(() => setPatient(null))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!id) return
    setTabLoading(true)
    const endpoints: Record<TabKey, string> = {
      visits: `/visits?patientId=${id}`,
      prescriptions: `/prescriptions?patientId=${id}`,
      'lab-reports': `/lab-reports?patientId=${id}`,
      vitals: `/vital-signs?patientId=${id}`,
      allergies: `/allergies?patientId=${id}`,
    }
    api.get(endpoints[activeTab])
      .then((r) => {
        const data = r.data
        setTabData(Array.isArray(data) ? data : (data?.items ?? []))
      })
      .catch(() => setTabData([]))
      .finally(() => setTabLoading(false))
  }, [id, activeTab])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-700" />
      </div>
    )
  }

  if (!patient) {
    return (
      <div className="text-center py-20 text-gray-500">
        <p>Patient not found.</p>
        <Link to="/patients" className="text-primary-600 hover:underline text-sm mt-2 inline-block">
          Back to Patients
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Link to="/patients" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{patient.name}</h2>
          <p className="text-sm text-gray-500 font-mono">{patient.patientUid}</p>
        </div>
        <Link
          to={`/emr/${patient.id}`}
          className="ml-auto text-sm bg-primary-50 text-primary-700 border border-primary-200 px-3 py-1.5 rounded-lg hover:bg-primary-100"
        >
          Full EMR Timeline
        </Link>
      </div>

      {/* Patient Info Card */}
      <Card>
        <div className="flex items-start gap-5">
          <div className="w-14 h-14 bg-primary-100 rounded-xl flex items-center justify-center shrink-0">
            <User className="w-7 h-7 text-primary-700" />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 flex-1">
            {[
              { label: 'Name', value: patient.name },
              { label: 'Mobile', value: patient.mobile },
              { label: 'Gender', value: patient.gender },
              { label: 'Blood Group', value: patient.bloodGroup || '-' },
              { label: 'Date of Birth', value: patient.dob ? format(new Date(patient.dob), 'dd MMM yyyy') : '-' },
              { label: 'Address', value: patient.address || '-' },
              { label: 'Registered', value: format(new Date(patient.createdAt), 'dd MMM yyyy') },
            ].map(({ label, value }) => (
              <div key={label}>
                <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">{label}</p>
                <p className="text-sm text-gray-800 font-medium mt-0.5">{value}</p>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ${
                activeTab === tab.key
                  ? 'border-primary-700 text-primary-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <Card>
        {tabLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-7 w-7 border-b-2 border-primary-700" />
          </div>
        ) : tabData.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No data found for this tab.</div>
        ) : (
          <div className="space-y-3">
            {activeTab === 'visits' &&
              (tabData as Visit[]).map((v) => (
                <div key={v.id} className="flex items-start justify-between p-4 bg-gray-50 rounded-lg border border-gray-100">
                  <div>
                    <p className="font-medium text-gray-800">{v.chiefComplaint}</p>
                    <p className="text-sm text-gray-500 mt-0.5">
                      {format(new Date(v.visitDate), 'dd MMM yyyy, hh:mm a')}
                    </p>
                    {v.aiSummary && <p className="text-sm text-gray-600 mt-1 italic">{v.aiSummary}</p>}
                  </div>
                  <div className="flex flex-col items-end gap-1.5">
                    <Badge status={v.status} />
                    <Link to={`/visits/${v.id}`} className="text-xs text-primary-600 hover:underline">
                      View detail →
                    </Link>
                  </div>
                </div>
              ))}

            {activeTab === 'prescriptions' &&
              (tabData as Prescription[]).map((p) => (
                <div key={p.id} className="p-4 bg-gray-50 rounded-lg border border-gray-100 flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Prescription #{p.id.slice(0, 8)}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {p.signedAt ? `Signed: ${format(new Date(p.signedAt), 'dd MMM yyyy')}` : 'Not yet signed'}
                    </p>
                    <p className="text-sm text-gray-700 mt-1">{p.items?.length ?? 0} medicine(s)</p>
                  </div>
                  <Badge status={p.status} />
                </div>
              ))}

            {activeTab === 'lab-reports' &&
              (tabData as LabReport[]).map((lr) => (
                <div key={lr.id} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-gray-800">{lr.reportType}</p>
                    {lr.isCritical && <Badge status="critical" label="Critical" />}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{format(new Date(lr.uploadedAt), 'dd MMM yyyy')}</p>
                  {lr.aiAnalysis && <p className="text-sm text-gray-600 mt-1.5 italic">{lr.aiAnalysis}</p>}
                </div>
              ))}

            {activeTab === 'vitals' &&
              (tabData as VitalSigns[]).map((vs) => (
                <div key={vs.id} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                  <div className="grid grid-cols-3 sm:grid-cols-5 gap-4">
                    {[
                      { label: 'BP', value: `${vs.bpSystolic}/${vs.bpDiastolic} mmHg` },
                      { label: 'Pulse', value: `${vs.pulse} bpm` },
                      { label: 'Temp', value: `${vs.temperature}°F` },
                      { label: 'SpO2', value: `${vs.spo2}%` },
                      { label: 'BMI', value: vs.bmi?.toFixed(1) ?? '-' },
                    ].map(({ label, value }) => (
                      <div key={label}>
                        <p className="text-xs text-gray-400 font-medium">{label}</p>
                        <p className="text-sm font-semibold text-gray-800">{value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}

            {activeTab === 'allergies' &&
              (tabData as Record<string, unknown>[]).map((a, i) => (
                <div key={i} className="p-4 bg-red-50 rounded-lg border border-red-100 text-sm text-red-800">
                  {String(a.allergen ?? a.description ?? JSON.stringify(a))}
                </div>
              ))}
          </div>
        )}
      </Card>
    </div>
  )
}
