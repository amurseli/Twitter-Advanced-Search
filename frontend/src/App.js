import React, { useState, useEffect } from 'react'
import { Button } from '../components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'

function App() {
  const [status, setStatus] = useState('checking...')
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    account: '',
    targets: '',
    start_date: '',
    end_date: '',
    query_type: 'from'
  })
  
  useEffect(() => {
    // Check backend status
    fetch('/api/health/')
      .then(res => res.json())
      .then(data => setStatus('Backend conectado ✅'))
      .catch(err => setStatus('Backend no disponible ❌'))
    
    // Load accounts and targets
    loadData()
  }, [])
  
  const loadData = async () => {
    try {
      // Cargar cuentas X
      const accountsRes = await fetch('/scraping/api/accounts/')
      console.log('Response status:', accountsRes.status)
      const accountsData = await accountsRes.json()
      console.log('Accounts data:', accountsData)
      setAccounts(accountsData.results || accountsData)
    } catch (error) {
      console.error('Error loading data:', error)
      setMessage('❌ Error cargando datos')
    }
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    
    try {
      // Formatear fechas con hora
      const startDate = new Date(formData.start_date)
      startDate.setHours(0, 0, 0, 0)
      
      const endDate = new Date(formData.end_date)
      endDate.setHours(23, 59, 59, 999)
      
      // Parsear usuarios del textarea
      const targetUsernames = formData.targets
        .split(/[\n,]/)
        .map(u => u.trim().replace('@', ''))
        .filter(u => u.length > 0)
      
      if (targetUsernames.length === 0) {
        throw new Error('Ingresá al menos un usuario')
      }
      
      const payload = {
        name: formData.name,
        account: parseInt(formData.account),
        target_usernames: targetUsernames,
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        query_type: formData.query_type
      }
      
      const response = await fetch('/scraping/api/jobs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })
      
      if (!response.ok) {
        throw new Error('Error al crear el job')
      }
      
      const job = await response.json()
      setMessage(`✅ Job "${job.name}" creado exitosamente! ID: ${job.id}`)
      
      // Reset form
      setFormData({
        name: '',
        account: '',
        targets: '',
        start_date: '',
        end_date: '',
        query_type: 'from'
      })
      
      // Opcional: iniciar el scraping automáticamente
      if (window.confirm('¿Querés iniciar el scraping ahora?')) {
        const startRes = await fetch(`/scraping/api/jobs/${job.id}/start/`, {
          method: 'POST'
        })
        if (startRes.ok) {
          setMessage(prev => prev + '\n🚀 Scraping iniciado!')
        }
      }
      
    } catch (error) {
      console.error('Error:', error)
      setMessage('❌ Error al crear el job: ' + error.message)
    } finally {
      setLoading(false)
    }
  }
  
  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }
  
  return React.createElement('div', { className: "min-h-screen bg-gray-50 p-8" },
    React.createElement('div', { className: "max-w-4xl mx-auto" },
      React.createElement('h1', { className: "text-3xl font-bold mb-8" }, 'X Advanced Search'),
      
      // Status Card
      React.createElement(Card, { className: "mb-6" },
        React.createElement(CardHeader, {},
          React.createElement(CardTitle, {}, 'Estado del Sistema')
        ),
        React.createElement(CardContent, {},
          React.createElement('p', {}, `Backend: ${status}`)
        )
      ),
      
      // Form Card
      React.createElement(Card, {},
        React.createElement(CardHeader, {},
          React.createElement(CardTitle, {}, 'Crear Trabajo de Scraping')
        ),
        React.createElement(CardContent, {},
          React.createElement('form', { onSubmit: handleSubmit },
            // Name input
            React.createElement('div', { className: "mb-4" },
              React.createElement('label', { className: "block text-sm font-medium mb-2" }, 'Nombre del trabajo'),
              React.createElement('input', {
                type: 'text',
                name: 'name',
                value: formData.name,
                onChange: handleInputChange,
                className: 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                placeholder: 'Ej: Tweets enero 2024',
                required: true
              })
            ),
            
            // Account select
            React.createElement('div', { className: "mb-4" },
              React.createElement('label', { className: "block text-sm font-medium mb-2" }, 'Cuenta X'),
              React.createElement('select', {
                name: 'account',
                value: formData.account,
                onChange: handleInputChange,
                className: 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                required: true
              },
                React.createElement('option', { value: '' }, 'Seleccionar cuenta...'),
                accounts.map(acc => 
                  React.createElement('option', { key: acc.id, value: acc.id }, `@${acc.username}`)
                )
              )
            ),
            
            // Targets textarea
            React.createElement('div', { className: "mb-4" },
              React.createElement('label', { className: "block text-sm font-medium mb-2" }, 'Usuarios objetivo'),
              React.createElement('textarea', {
                name: 'targets',
                value: formData.targets,
                onChange: handleInputChange,
                className: 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                placeholder: '@usuario1\n@usuario2\n@usuario3',
                rows: 4,
                required: true
              }),
              React.createElement('p', { className: "text-sm text-gray-500 mt-1" }, 
                'Un usuario por línea o separados por comas. El @ es opcional.')
            ),
            
            // Date inputs
            React.createElement('div', { className: "grid grid-cols-2 gap-4 mb-4" },
              React.createElement('div', {},
                React.createElement('label', { className: "block text-sm font-medium mb-2" }, 'Fecha desde'),
                React.createElement('input', {
                  type: 'date',
                  name: 'start_date',
                  value: formData.start_date,
                  onChange: handleInputChange,
                  className: 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                  required: true
                })
              ),
              React.createElement('div', {},
                React.createElement('label', { className: "block text-sm font-medium mb-2" }, 'Fecha hasta'),
                React.createElement('input', {
                  type: 'date',
                  name: 'end_date',
                  value: formData.end_date,
                  onChange: handleInputChange,
                  className: 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                  required: true
                })
              )
            ),
            
            // Query type radio buttons
            React.createElement('div', { className: "mb-6" },
              React.createElement('label', { className: "block text-sm font-medium mb-2" }, 'Tipo de búsqueda'),
              React.createElement('div', { className: "space-y-2" },
                [
                  { value: 'from', label: 'Tweets DE estos usuarios' },
                  { value: 'to', label: 'Tweets HACIA estos usuarios' },
                  { value: 'mentioning', label: 'Tweets que MENCIONAN a estos usuarios' }
                ].map(option =>
                  React.createElement('label', { 
                    key: option.value,
                    className: "flex items-center cursor-pointer"
                  },
                    React.createElement('input', {
                      type: 'radio',
                      name: 'query_type',
                      value: option.value,
                      checked: formData.query_type === option.value,
                      onChange: handleInputChange,
                      className: 'mr-2'
                    }),
                    React.createElement('span', {}, option.label)
                  )
                )
              )
            ),
            
            // Message
            message && React.createElement('div', {
              className: `mb-4 p-3 rounded ${message.includes('✅') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`
            }, message.split('\n').map((line, i) => 
              React.createElement('div', { key: i }, line)
            )),
            
            // Submit button
            React.createElement(Button, {
              type: 'submit',
              disabled: loading,
              className: 'w-full'
            }, loading ? 'Creando...' : 'Crear Trabajo de Scraping')
          )
        )
      )
    )
  )
}

export default App