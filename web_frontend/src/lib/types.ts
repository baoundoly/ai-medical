export interface User {
  id: string
  email: string
  fullName: string
  role: string
  tenantId: string
}

export interface Patient {
  id: string
  patientUid: string
  name: string
  mobile: string
  gender: string
  bloodGroup: string
  dob: string
  address: string
  createdAt: string
}

export interface Visit {
  id: string
  patientId: string
  doctorId: string
  visitDate: string
  status: string
  chiefComplaint: string
  aiSummary: string
  doctorApprovedAt: string | null
}

export interface Appointment {
  id: string
  patientId: string
  doctorId: string
  scheduledAt: string
  appointmentType: string
  status: string
  tokenNumber: number
  isEmergency: boolean
}

export interface PrescriptionItem {
  id: string
  medicineName: string
  dosage: string
  frequency: string
  duration: string
  mealInstruction: string
}

export interface Prescription {
  id: string
  visitId: string
  patientId: string
  doctorId: string
  status: string
  signedAt: string | null
  items: PrescriptionItem[]
}

export interface VitalSigns {
  id: string
  visitId: string
  bpSystolic: number
  bpDiastolic: number
  pulse: number
  temperature: number
  spo2: number
  weight: number
  height: number
  bmi: number
}

export interface LabReport {
  id: string
  patientId: string
  reportType: string
  isCritical: boolean
  uploadedAt: string
  aiAnalysis: string
}

export interface Invoice {
  id: string
  patientId: string
  totalAmount: number
  netAmount: number
  status: string
}

export interface ApiListResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}
