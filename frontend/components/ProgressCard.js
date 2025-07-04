import React, { useState, useEffect } from 'react'
import { Card } from './ui/card'
import { CircularProgress } from './ui/progress'

// Agregar estos estilos al archivo CSS global o crear un style tag
const styles = `
  @keyframes pulse-subtle {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
  }
  
  @keyframes spin-slow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .animate-pulse-subtle {
    animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  
  .animate-spin-slow {
    animation: spin-slow 3s linear infinite;
  }
`

// Inyectar estilos si no existen
if (typeof document !== 'undefined' && !document.getElementById('progress-card-styles')) {
  const styleSheet = document.createElement('style')
  styleSheet.id = 'progress-card-styles'
  styleSheet.textContent = styles
  document.head.appendChild(styleSheet)
}

const statusConfig = {
  idle: { icon: '⏸️', color: 'text-gray-500', bgColor: 'bg-gray-50' },
  starting: { icon: '🚀', color: 'text-blue-500', bgColor: 'bg-blue-50' },
  running: { icon: '⚙️', color: 'text-blue-600', bgColor: 'bg-blue-50' },
  downloading: { icon: '💾', color: 'text-green-600', bgColor: 'bg-green-50' },
  completed: { icon: '✅', color: 'text-green-600', bgColor: 'bg-green-50' },
  failed: { icon: '❌', color: 'text-red-600', bgColor: 'bg-red-50' }
}

export function ProgressCard({ status, messages, onClose }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [progress, setProgress] = useState(0)
  
  useEffect(() => {
    const progressMap = {
      idle: 0,
      starting: 20,
      running: 50,
      downloading: 80,
      completed: 100,
      failed: 100
    }
    setProgress(progressMap[status] || 0)
  }, [status])
  
  if (status === 'idle') return null
  
  const config = statusConfig[status] || statusConfig.idle
  const isActive = ['starting', 'running', 'downloading'].includes(status)
  
  return React.createElement(Card, {
    className: `fixed bottom-4 right-4 w-96 transition-all duration-300 shadow-lg ${config.bgColor} ${isActive ? 'animate-pulse-subtle' : ''}`,
    style: { maxHeight: isExpanded ? '400px' : '80px' }
  },
    React.createElement('div', {
      className: 'p-4 cursor-pointer',
      onClick: () => setIsExpanded(!isExpanded)
    },
      React.createElement('div', { className: 'flex items-center justify-between' },
        React.createElement('div', { className: 'flex items-center space-x-3' },
          React.createElement(CircularProgress, {
            value: progress,
            size: 40,
            showValue: !isActive,
            className: isActive ? 'animate-spin-slow' : ''
          }),
          React.createElement('div', {},
            React.createElement('div', { className: 'flex items-center space-x-2' },
              React.createElement('span', { className: 'text-lg' }, config.icon),
              React.createElement('span', { className: `font-medium ${config.color}` },
                status === 'starting' ? 'Iniciando scraping...' :
                status === 'running' ? 'Procesando tweets...' :
                status === 'downloading' ? 'Descargando JSON...' :
                status === 'completed' ? 'Completado!' :
                status === 'failed' ? 'Error en el proceso' :
                'Procesando...'
              )
            ),
            messages.length > 0 && React.createElement('p', { 
              className: 'text-sm text-gray-600 mt-1 truncate' 
            }, messages[messages.length - 1])
          )
        ),
        React.createElement('button', {
          className: 'text-gray-400 hover:text-gray-600 transition-colors',
          onClick: (e) => {
            e.stopPropagation()
            setIsExpanded(!isExpanded)
          }
        }, 
          status === 'completed' || status === 'failed' ? 
            (isExpanded ? '▼' : '▲') : 
            (isExpanded ? '▼' : '▲')
        )
      )
    ),
    
    isExpanded && React.createElement('div', {
      className: 'px-4 pb-4 max-h-80 overflow-y-auto'
    },
      React.createElement('div', { className: 'border-t pt-3 mt-2' },
        React.createElement('div', { className: 'space-y-2' },
          messages.map((msg, index) => {
            const isError = msg.includes('❌')
            const isSuccess = msg.includes('✅')
            const isInfo = msg.includes('🚀') || msg.includes('⏳')
            
            return React.createElement('div', {
              key: index,
              className: `text-sm py-1 px-2 rounded ${
                isError ? 'bg-red-100 text-red-700' :
                isSuccess ? 'bg-green-100 text-green-700' :
                isInfo ? 'bg-blue-100 text-blue-700' :
                'bg-gray-100 text-gray-700'
              }`
            }, msg)
          })
        )
      ),
      
      (status === 'completed' || status === 'failed') && 
      React.createElement('div', { className: 'mt-4 pt-3 border-t' },
        React.createElement('button', {
          className: 'w-full py-2 px-4 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors text-sm font-medium',
          onClick: onClose
        }, 'Cerrar')
      )
    )
  )
}