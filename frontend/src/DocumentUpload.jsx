import { useState } from 'react'
import { uploadDocument } from './api'

function DocumentUpload({ conversationId, onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const validTypes = ['application/pdf', 'text/plain']
      const validExtensions = ['.pdf', '.txt']
      
      const fileExt = '.' + selectedFile.name.split('.').pop().toLowerCase()
      
      if (!validTypes.includes(selectedFile.type) && !validExtensions.includes(fileExt)) {
        setError('Please upload a PDF or TXT file')
        setFile(null)
        return
      }
      
      setError(null)
      setFile(selectedFile)
    }
  }

  const handleUpload = async () => {
    if (!file || !conversationId) return

    setUploading(true)
    setError(null)

    try {
      const result = await uploadDocument(conversationId, file)
      setFile(null)
      if (onUploadSuccess) {
        onUploadSuccess(result.data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="document-upload">
      <input
        type="file"
        accept=".pdf,.txt"
        onChange={handleFileChange}
        disabled={uploading}
        className="file-input"
      />
      {file && (
        <div className="file-info">
          <span className="file-name">{file.name}</span>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="upload-btn"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default DocumentUpload
