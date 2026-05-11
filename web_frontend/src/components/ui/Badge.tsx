type BadgeVariant = 'green' | 'yellow' | 'red' | 'blue' | 'gray' | 'purple'

const colorMap: Record<string, BadgeVariant> = {
  active: 'green',
  approved: 'green',
  completed: 'green',
  signed: 'green',
  paid: 'green',
  pending: 'yellow',
  scheduled: 'blue',
  'in-progress': 'blue',
  draft: 'gray',
  cancelled: 'red',
  critical: 'red',
  emergency: 'red',
  normal: 'gray',
  partial: 'purple',
}

const variantClasses: Record<BadgeVariant, string> = {
  green: 'bg-green-100 text-green-800',
  yellow: 'bg-yellow-100 text-yellow-800',
  red: 'bg-red-100 text-red-800',
  blue: 'bg-blue-100 text-blue-800',
  gray: 'bg-gray-100 text-gray-700',
  purple: 'bg-purple-100 text-purple-800',
}

interface BadgeProps {
  status: string
  label?: string
  className?: string
}

export default function Badge({ status, label, className = '' }: BadgeProps) {
  const variant: BadgeVariant = colorMap[status.toLowerCase()] ?? 'gray'
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}
    >
      {label ?? status}
    </span>
  )
}
