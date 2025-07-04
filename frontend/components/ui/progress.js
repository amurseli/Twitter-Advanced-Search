import React from 'react'

export function Progress({ value = 0, className = '', ...props }) {
  return React.createElement('div', {
    className: `relative h-4 w-full overflow-hidden rounded-full bg-gray-100 ${className}`,
    ...props
  },
    React.createElement('div', {
      className: 'h-full w-full flex-1 bg-blue-600 transition-all duration-300 ease-in-out',
      style: { transform: `translateX(-${100 - (value || 0)}%)` }
    })
  )
}

export function CircularProgress({ value = 0, size = 40, strokeWidth = 4, className = '' }) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (value / 100) * circumference

  return React.createElement('div', { className: `relative ${className}` },
    React.createElement('svg', {
      className: 'transform -rotate-90',
      width: size,
      height: size
    },
      React.createElement('circle', {
        className: 'text-gray-200',
        strokeWidth: strokeWidth,
        stroke: 'currentColor',
        fill: 'transparent',
        r: radius,
        cx: size / 2,
        cy: size / 2
      }),
      React.createElement('circle', {
        className: 'text-blue-600 transition-all duration-300 ease-in-out',
        strokeWidth: strokeWidth,
        strokeDasharray: circumference,
        strokeDashoffset: offset,
        strokeLinecap: 'round',
        stroke: 'currentColor',
        fill: 'transparent',
        r: radius,
        cx: size / 2,
        cy: size / 2
      })
    ),
    value !== undefined && React.createElement('span', {
      className: 'absolute inset-0 flex items-center justify-center text-xs font-medium'
    }, `${Math.round(value)}%`)
  )
}