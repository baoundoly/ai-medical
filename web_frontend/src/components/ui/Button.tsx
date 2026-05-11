import React from 'react'
import { Loader2 } from 'lucide-react'

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
  children: React.ReactNode
}

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-primary-700 text-white hover:bg-primary-800 focus:ring-primary-500 border-transparent',
  secondary:
    'bg-white text-gray-700 hover:bg-gray-50 focus:ring-primary-500 border-gray-300',
  danger:
    'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 border-transparent',
  ghost:
    'bg-transparent text-gray-600 hover:bg-gray-100 focus:ring-gray-400 border-transparent',
}

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-5 py-2.5 text-base',
}

export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  className = '',
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 rounded-lg border font-medium
        transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1
        disabled:opacity-60 disabled:cursor-not-allowed
        ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  )
}
