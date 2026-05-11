import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Plus, Search, X, ChevronLeft, ChevronRight } from 'lucide-react'
import api from '../lib/api'
import type { Patient } from '../lib/types'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Table, { Column } from '../components/ui/Table'
import { format } from 'date-fns'

interface NewPatientForm {
  name: string
  mobile: string
  gender: string
  bloodGroup: string
  dob: string
  address: string
}

const PAGE_SIZE = 15

export default function PatientsPage() {
  const navigate = useNavigate()
  const [patients, setPatients] = useState<Patient[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [apiError, setApiError] = useState('')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<NewPatientForm>()

  const fetchPatients = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page, pageSize: PAGE_SIZE }
      if (search) params.search = search
      const res = await api.get('/patients', { params })
      const data = res.data
      if (Array.isArray(data)) {
        setPatients(data)
        setTotal(data.length)
      } else {
        setPatients(data.items ?? [])
        setTotal(data.total ?? 0)
      }
    } catch {
      setPatients([])
    } finally {
      setLoading(false)
    }
  }, [page, search])

  useEffect(() => {
    fetchPatients()
  }, [fetchPatients])

  const onSubmit = async (data: NewPatientForm) => {
    setApiError('')
    setSubmitting(true)
    try {
      await api.post('/patients', data)
      reset()
      setShowModal(false)
      fetchPatients()
    } catch {
      setApiError('Failed to register patient. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const columns: Column<Record<string, unknown>>[] = [
    { key: 'patientUid', header: 'Patient UID', render: (v) => (
      <span className="font-mono text-xs bg-gray-100 px-2 py-0.5 rounded">{String(v ?? '')}</span>
    )},
    { key: 'name', header: 'Name', render: (v, row) => (
      <button
        onClick={() => navigate(`/patients/${(row as unknown as Patient).id}`)}
        className="font-medium text-primary-700 hover:underline"
      >
        {String(v ?? '')}
      </button>
    )},
    { key: 'mobile', header: 'Mobile' },
    { key: 'gender', header: 'Gender', render: (v) => (
      <span className="capitalize">{String(v ?? '')}</span>
    )},
    { key: 'bloodGroup', header: 'Blood Group', render: (v) => (
      <span className="font-semibold text-red-700">{String(v ?? '-')}</span>
    )},
    { key: 'createdAt', header: 'Registered', render: (v) => (
      <span className="text-gray-500">
        {v ? format(new Date(String(v)), 'dd MMM yyyy') : '-'}
      </span>
    )},
  ]

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Patients</h2>
          <p className="text-sm text-gray-500 mt-0.5">{total} total patients</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4" />
          New Patient
        </Button>
      </div>

      <Card>
        {/* Search */}
        <div className="mb-4 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or mobile..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full sm:w-80 pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <Table columns={columns} data={patients as Record<string, unknown>[]} loading={loading} emptyMessage="No patients found." />

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
            <p className="text-sm text-gray-500">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </Button>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* New Patient Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900">Register New Patient</h3>
              <button onClick={() => { setShowModal(false); reset() }} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-5 space-y-4">
              {apiError && (
                <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{apiError}</p>
              )}
              <Input
                label="Full Name"
                placeholder="Patient full name"
                error={errors.name?.message}
                {...register('name', { required: 'Name is required' })}
              />
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Mobile"
                  placeholder="01XXXXXXXXX"
                  error={errors.mobile?.message}
                  {...register('mobile', { required: 'Mobile is required' })}
                />
                <Input
                  label="Date of Birth"
                  type="date"
                  error={errors.dob?.message}
                  {...register('dob', { required: 'DOB is required' })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">Gender</label>
                  <select
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('gender', { required: true })}
                  >
                    <option value="">Select</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">Blood Group</label>
                  <select
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('bloodGroup')}
                  >
                    <option value="">Unknown</option>
                    {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map((bg) => (
                      <option key={bg} value={bg}>{bg}</option>
                    ))}
                  </select>
                </div>
              </div>
              <Input
                label="Address"
                placeholder="Village, Upazila, District"
                {...register('address')}
              />
              <div className="flex justify-end gap-3 pt-2">
                <Button variant="secondary" type="button" onClick={() => { setShowModal(false); reset() }}>
                  Cancel
                </Button>
                <Button type="submit" loading={submitting}>
                  Register Patient
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
