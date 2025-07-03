import React from 'react'

export function Card({ className = '', ...props }) {
  return React.createElement('div', {
    className: `rounded-lg border border-gray-200 bg-white shadow-sm ${className}`,
    ...props
  })
}

export function CardHeader({ className = '', ...props }) {
  return React.createElement('div', {
    className: `flex flex-col space-y-1.5 p-6 ${className}`,
    ...props
  })
}

export function CardTitle({ className = '', ...props }) {
  return React.createElement('h3', {
    className: `text-2xl font-semibold leading-none tracking-tight ${className}`,
    ...props
  })
}

export function CardContent({ className = '', ...props }) {
  return React.createElement('div', {
    className: `p-6 pt-0 ${className}`,
    ...props
  })
}
