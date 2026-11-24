function DocumentList({ documents, onDeleteDocument }) {
  const handleDelete = async (documentId) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return
    }

    // UseChats.handleDocumentDelete calls the API and updates the list
    if (onDeleteDocument) {
      await onDeleteDocument(documentId)
    }
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="document-list empty">
        <p>No documents uploaded</p>
      </div>
    )
  }

  return (
    <div className="document-list">
      <h3>Uploaded Documents</h3>
      <ul className="document-items">
        {documents.map((doc) => (
          <li key={doc._id} className="document-item">
            <div className="document-info">
              <span className="document-name">{doc.filename}</span>
              <span className="document-type">{doc.file_type}</span>
              <span className="document-chunks">{doc.total_chunks} chunks</span>
            </div>
            <button
              onClick={() => handleDelete(doc._id)}
              className="delete-btn"
              title="Delete document"
            >
              ×
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default DocumentList
