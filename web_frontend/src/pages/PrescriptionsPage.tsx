import { useEffect, useState, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { PenLine, AlertTriangle, X, ShieldAlert } from 'lucide-react'
import api from '../lib/api'
import type { Prescription } from '../lib/types'
import { useAuth } from '../contexts/AuthContext'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Input from '../components/ui/Input'
import { format } from 'date-fns'

interface SignForm {
  password: string
}

export default function PrescriptionsPage() {
  const { user } = useAuth()
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([])
  const [loading, setLoading] = useState(true)
  const [signingId, setSigningId] = useState<string | null>(null)
  const [signError, setSignError] = useState('')
  const [signing, setSigning] = useState(false)
  const [drugWarnings, setDrugWarnings] = useState<Record<string, string[]>>({})

  const { register, handleSubmit, reset, formState: { errors } } = useForm<SignForm>()

  const fetchPrescriptions = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/prescriptions')
      const data = res.data
      const items: Prescription[] = Array.isArray(data) ? data : (data?.items ?? [])
      setPrescriptions(items)

      // Fetch drug interactions for unsigned prescriptions
      const warnings: Record<string, string[]> = {}
      await Promise.allSettled(
        items
          .filter((p) => p.status !== 'signed' && p.items?.length > 1)
          .map(async (p) => {
            try {
              const res = await api.get(`/prescriptions/${p.id}/drug-interactions`)
              if (res.data?.warnings?.length > 0) {
                warnings[p.id] = res.data.warnings
              }
            } catch {
              // ignore
            }
          }),
      )
      setDrugWarnings(warnings)
    } catch {
      setPrescriptions([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchPrescriptions() }, [fetchPrescriptions])

  const handleSign = async ({ password }: SignForm) => {
    if (!signingId) return
    setSignError('')
    setSigning(true)
    try {
      await api.post(`/prescriptions/${signingId}/sign`, { password })
      reset()
      setSigningId(null)
      fetchPrescriptions()
    } catch {
      setSignError('Failed to sign. Check your password and try again.')
    } finally {
      setSigning(false)
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Prescriptions</h2>
        <p className="text-sm text-gray-500 mt-0.5">{prescriptions.length} prescriptions</p>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <div key={i} className="h-32 bg-gray-100 rounded-xl animate-pulse" />)}
        </div>
      ) : prescriptions.length === 0 ? (
        <Card>
          <p className="text-center py-10 text-gray-400">No prescriptions found.</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {prescriptions.map((p) => (
            <Card key={p.id}>
              {/* Drug warnings */}
              {drugWarnings[p.id]?.length > 0 && (
                <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-3 flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-yellow-800">Drug Interaction Warning</p>
                    <ul className="mt-1 space-y-0.5">
                      {drugWarnings[p.id].map((w, i) => (
                        <li key={i} className="text-xs text-yellow-700">{w}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-gray-900">Prescription #{p.id.slice(0, 8)}</p>
                    <Badge status={p.status} />
                  </div>
                  <p className="text-sm text-gray-500 mt-0.5">
                    {p.signedAt
                      ? `Signed: ${format(new Date(p.signedAt), 'dd MMM yyyy, hh:mm a')}`
                      : 'Unsigned'}
                  </p>
                </div>
                {user?.role === 'Doctor' && p.status !== 'signed' && (
                  <Button size="sm" onClick={() => setSigningId(p.id)}>
                    <PenLine className="w-3.5 h-3.5" />
                    Sign
                  </Button>
                )}
              </div>

              {/* Medicine table */}
              {p.items?.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs text-gray-400 border-b border-gray-100">
                        <th className="pb-2 pr-4">Medicine</th>
                        <th className="pb-2 pr-4">Dosage</th>
                        <th className="pb-2 pr-4">Frequency</th>
                        <th className="pb-2 pr-4">Duration</th>
                        <th className="pb-2">Meal</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {p.items.map((item) => (
                        <tr key={item.id} className="hover:bg-gray-50">
                          <td className="py-2 pr-4 font-medium text-gray-800">{item.medicineName}</td>
                          <td className="py-2 pr-4 text-gray-600">{item.dosage}</td>
                          <td className="py-2 pr-4 text-gray-600">{item.frequency}</td>
                          <td className="py-2 pr-4 text-gray-600">{item.duration}</td>
                          <td className="py-2 text-gray-600">{item.mealInstruction}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}

      {/* Sign Modal */}
      {signingId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-primary-700" />
                <h3 className="text-lg font-semibold">Confirm Signature</h3>
              </div>
              <button onClick={() => { setSigningId(null); reset() }} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit(handleSign)} className="px-6 py-5 space-y-4">
              <p className="text-sm text-gray-600">Enter your password to digitally sign this prescription.</p>
              {signError && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{signError}</p>}
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                error={errors.password?.message}
                {...register('password', { required: 'Password is required' })}
              />
              <div className="flex justify-end gap-3">
                <Button variant="secondary" type="button" onClick={() => { setSigningId(null); reset() }}>
                  Cancel
                </Button>
                <Button type="submit" loading={signing}>
                  Sign Prescription
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
