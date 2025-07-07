import React, { useState } from 'react'

function App() {
  const [buttonState, setButtonState] = useState('create')
  const [statusMessage, setStatusMessage] = useState({ text: '', type: '' })
  const [downloadData, setDownloadData] = useState(null)
  
  const [formData, setFormData] = useState({
    targets: '',
    start_date: '',
    end_date: '',
    query_type: 'from',
    export_format: 'json'
  })
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (buttonState === 'download' && downloadData) {
      const blob = await downloadData.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = downloadData.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      setTimeout(() => {
        setButtonState('create')
        setStatusMessage({ text: '', type: '' })
        setDownloadData(null)
        setFormData({
          targets: '',
          start_date: '',
          end_date: '',
          query_type: 'from',
          export_format: 'json'
        })
      }, 1000)
      
      return
    }
    
    if (buttonState !== 'create') return
    
    setButtonState('processing')
    setStatusMessage({ text: 'El trabajo se está procesando. Esto puede tomar unos minutos...', type: 'info' })
    
    try {
      const startDate = new Date(formData.start_date)
      startDate.setHours(0, 0, 0, 0)
      
      const endDate = new Date(formData.end_date)
      endDate.setHours(23, 59, 59, 999)
      
      const targetUsernames = formData.targets
        .split(/[\n,]/)
        .map(u => u.trim().replace('@', ''))
        .filter(u => u.length > 0)
      
      if (targetUsernames.length === 0) {
        throw new Error('Ingresá al menos un usuario')
      }
      
      const payload = {
        name: `Job ${new Date().toISOString()}`,
        target_usernames: targetUsernames,
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        query_type: formData.query_type,
        export_format: formData.export_format
      }
      
      const response = await fetch('/scraping/api/jobs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })
      
      const responseData = await response.json()
      
      if (!response.ok) {
        if (responseData && typeof responseData === 'object') {
          const errorMessages = []
          for (const [field, errors] of Object.entries(responseData)) {
            if (Array.isArray(errors)) {
              errorMessages.push(`${field}: ${errors.join(', ')}`)
            } else {
              errorMessages.push(`${field}: ${errors}`)
            }
          }
          throw new Error(errorMessages.join('\n'))
        }
        throw new Error('Error al crear el job')
      }
      
      const startRes = await fetch(`/scraping/api/jobs/${responseData.id}/start/`, {
        method: 'POST'
      })
      
      if (!startRes.ok) {
        throw new Error('Error al iniciar el scraping')
      }
      
      const checkStatus = async () => {
        const statusRes = await fetch(`/scraping/api/jobs/${responseData.id}/`)
        const jobData = await statusRes.json()
        
        if (jobData.status === 'completed') {
          const downloadRes = await fetch(`/scraping/api/jobs/${responseData.id}/download/`)
          
          if (downloadRes.ok) {
            const extension = formData.export_format === 'csv' ? 'csv' : 'json'
            setDownloadData({
              blob: () => downloadRes.blob(),
              filename: `tweets_job_${responseData.id}.${extension}`
            })
            
            setButtonState('download')
            setStatusMessage({ 
              text: `Trabajo completado! ${jobData.tweets_count || 0} tweets encontrados.`, 
              type: 'success' 
            })
          } else {
            throw new Error('Error al preparar la descarga')
          }
          
          return true
        } else if (jobData.status === 'failed') {
          throw new Error(jobData.error_message || 'El scraping falló')
        }
        
        return false
      }
      
      const pollInterval = setInterval(async () => {
        try {
          const isDone = await checkStatus()
          if (isDone) {
            clearInterval(pollInterval)
          }
        } catch (error) {
          clearInterval(pollInterval)
          setButtonState('create')
          setStatusMessage({ text: error.message, type: 'error' })
        }
      }, 2000)
      
      setTimeout(() => {
        clearInterval(pollInterval)
        if (buttonState === 'processing') {
          setButtonState('create')
          setStatusMessage({ text: 'Timeout - verificá el estado en el admin', type: 'error' })
        }
      }, 300000)
      
    } catch (error) {
      console.error('Error:', error)
      setButtonState('create')
      setStatusMessage({ text: error.message, type: 'error' })
    }
  }
  
  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }
  
  const getButtonContent = () => {
    switch (buttonState) {
      case 'processing':
        return React.createElement(React.Fragment, {},
          React.createElement('span', { className: 'spinner' }),
          'Procesando...'
        )
      case 'download':
        return 'Descargar Resultados'
      default:
        return 'Buscar Tweets'
    }
  }
  
  const getButtonClass = () => {
    switch (buttonState) {
      case 'processing':
        return 'btn-primary btn-processing'
      case 'download':
        return 'btn-primary btn-download'
      default:
        return 'btn-primary btn-create'
    }
  }
  
  const getQueryTypeHelp = () => {
    switch (formData.query_type) {
      case 'from':
        return 'Buscar tweets publicados POR estos usuarios'
      case 'to':
        return 'Buscar tweets dirigidos A estos usuarios (respuestas)'
      case 'mentioning':
        return 'Buscar tweets que MENCIONEN a estos usuarios'
      default:
        return ''
    }
  }
  
  return React.createElement('div', { className: 'app-container' },
    React.createElement('div', { className: 'content-wrapper' },
      React.createElement('h1', { className: 'app-logo' }, 'Búsqueda Avanzada de Tweets'),
      
      React.createElement('div', { className: 'form-card' },
        
        React.createElement('form', { onSubmit: handleSubmit },
          
          React.createElement('div', { className: 'form-group' },
            React.createElement('label', { className: 'form-label' }, 'Usuarios objetivo'),
            React.createElement('textarea', {
              name: 'targets',
              value: formData.targets,
              onChange: handleInputChange,
              className: 'form-textarea',
              placeholder: '@usuario1\n@usuario2\n@usuario3',
              required: true,
              disabled: buttonState !== 'create'
            }),
            React.createElement('p', { className: 'form-help' }, 'Un usuario por línea, con o sin @')
          ),
          
          React.createElement('div', { className: 'date-group' },
            React.createElement('div', { className: 'form-group' },
              React.createElement('label', { className: 'form-label' }, 'Fecha desde'),
              React.createElement('input', {
                type: 'date',
                name: 'start_date',
                value: formData.start_date,
                onChange: handleInputChange,
                className: 'form-input',
                required: true,
                disabled: buttonState !== 'create'
              })
            ),
            React.createElement('div', { className: 'form-group' },
              React.createElement('label', { className: 'form-label' }, 'Fecha hasta'),
              React.createElement('input', {
                type: 'date', 
                name: 'end_date',
                value: formData.end_date,
                onChange: handleInputChange,
                className: 'form-input',
                required: true,
                disabled: buttonState !== 'create'
              })
            )
          ),
          
          React.createElement('div', { className: 'form-group' },
            React.createElement('label', { className: 'form-label' }, 'Tipo de búsqueda'),
            React.createElement('div', { className: 'query-type-selector' },
              [
                { value: 'from', label: 'DE' },
                { value: 'to', label: 'HACIA' },
                { value: 'mentioning', label: 'MENCIONANDO' }
              ].map(option =>
                React.createElement('button', {
                  key: option.value,
                  type: 'button',
                  className: `query-type-option ${formData.query_type === option.value ? 'active' : ''}`,
                  onClick: () => handleInputChange({ target: { name: 'query_type', value: option.value } }),
                  disabled: buttonState !== 'create'
                }, option.label)
              )
            ),
            React.createElement('p', { className: 'query-type-help' }, getQueryTypeHelp())
          ),
          
          React.createElement('div', { className: 'form-group' },
            React.createElement('label', { className: 'form-label' }, 'Formato de exportación'),
            React.createElement('div', { className: 'format-selector' },
              [
                { value: 'json', label: 'JSON' },
                { value: 'csv', label: 'CSV' }
              ].map(option =>
                React.createElement('button', {
                  key: option.value,
                  type: 'button',
                  className: `format-option ${formData.export_format === option.value ? 'active' : ''}`,
                  onClick: () => handleInputChange({ target: { name: 'export_format', value: option.value } }),
                  disabled: buttonState !== 'create'
                }, option.label)
              )
            )
          ),
          
          React.createElement('button', {
            type: 'submit',
            className: getButtonClass(),
            disabled: buttonState === 'processing'
          }, getButtonContent()),
          
          statusMessage.text && React.createElement('div', {
            className: `status-message ${statusMessage.type}`
          }, statusMessage.text)
        )
      )
    )
  )
}

export default App