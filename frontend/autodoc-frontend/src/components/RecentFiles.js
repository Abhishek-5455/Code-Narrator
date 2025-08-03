import React, { useState, useEffect } from 'react';
import './RecentFiles.css';

const RecentFiles = ({ refreshTrigger, onFileSelect }) => {
  const [recentFiles, setRecentFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const API_BASE_URL = 'http://localhost:8000';

  useEffect(() => {
    fetchRecentFiles();
  }, [refreshTrigger]);

  const fetchRecentFiles = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/files/recent?limit=20`);
      const data = await response.json();
      
      if (response.ok) {
        setRecentFiles(data.recent_files || []);
      } else {
        setError('Failed to fetch recent files');
      }
    } catch (error) {
      console.error('Error fetching recent files:', error);
      setError('Unable to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileClick = async (file) => {
    try {
      const fileExtension = file.filename.split('.').pop().toLowerCase();
      
      // Check if it's a markdown file
      if (fileExtension === 'md') {
        // Download the markdown file directly
        const response = await fetch(`${API_BASE_URL}/files/${file.file_id}/download`);
        if (response.ok) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = file.filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        } else {
          console.error('Failed to download markdown file');
        }
      } else if (['py', 'java', 'js', 'jsx'].includes(fileExtension)) {
        // Handle source code files - fetch content and regenerate documentation/suggestions
        const response = await fetch(`${API_BASE_URL}/files/${file.file_id}`);
        const data = await response.json();
        
        if (response.ok) {
          // Create a proper File object from the cached content
          const fileContent = data.content || data.file_content || '';
          const blob = new Blob([fileContent], { type: getFileType(data.filename) });
          const fileObject = new File([blob], data.filename, { type: getFileType(data.filename) });
          
          // Send the file to parse-code endpoint to regenerate documentation
          const formData = new FormData();
          formData.append('file', fileObject);
          
          try {
            const parseResponse = await fetch(`${API_BASE_URL}/parse-code/`, {
              method: 'POST',
              body: formData,
            });
            
            const parseData = await parseResponse.json();
            
            if (parseResponse.ok && !parseData.error) {
              // Successfully regenerated documentation, now call onFileSelect with the new content
              onFileSelect(fileObject, parseData.markdown_content, parseData.language);
            } else {
              console.error('Failed to regenerate documentation:', parseData.message || 'Unknown error');
              alert('Failed to regenerate documentation. Please try again.');
            }
          } catch (parseError) {
            console.error('Error regenerating documentation:', parseError);
            alert('Failed to regenerate documentation. Please check if the backend server is running.');
          }
        }
      } else {
        // For other file types, just show a message
        alert(`File type .${fileExtension} is not supported for documentation generation.`);
      }
    } catch (error) {
      console.error('Error loading file:', error);
      alert('Failed to load file. Please try again.');
    }
  };

  const getFileType = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    switch (ext) {
      case 'py': return 'text/x-python';
      case 'java': return 'text/x-java';
      case 'js':
      case 'jsx': return 'text/javascript';
      default: return 'text/plain';
    }
  };

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    
    switch (ext) {
      case 'py':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="#3776ab" stroke="none">
            <path d="M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.26-.02.2-.01h4.22l.41-.04.31-.08.29-.12.25-.15.22-.17.18-.19.13-.21.1-.21.06-.23.06-.21.02-.17.01-.13V2.5l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V-.02l.01-.13.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h1.06l.22.02z"/>
          </svg>
        );
      case 'java':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="#ed8b00" stroke="none">
            <path d="M8.851 18.56s-.917.534.653.714c1.902.218 2.874.187 4.969-.211 0 0 .552.346 1.321.646-4.699 2.013-10.633-.118-6.943-1.149M8.276 15.933s-1.028.761.542.924c2.032.209 3.636.227 6.413-.308 0 0 .384.389.987.602-5.679 1.661-12.007.13-7.942-1.218"/>
          </svg>
        );
      case 'js':
      case 'jsx':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="#f7df1e" stroke="none">
            <rect width="24" height="24" rx="2" fill="#f7df1e"/>
            <path d="M17.09 18.42c-.52-1.28-1.56-2.36-4.13-3.37-.74-.29-1.56-.49-1.8-1.07-.09-.36-.11-.56-.05-.78.17-.72.97-.93 1.6-.73.42.13.8.46 1.04.99 1.11-.72 1.11-.72 1.87-1.2-.29-.45-.43-.64-.62-.83-.67-.72-1.56-1.08-3.01-1.05l-.75.09c-.72.18-1.4.56-1.81 1.08-.74.74-.74 1.94-.03 2.59.74.68 2.04 1 1.8 1.8-.22.79-1.01.79-2.27.2-.64-.29-1-.72-1.38-1.65l-1.94 1.11c.22.49.36.71.65 1.14 1.5 1.65 5.24 1.56 5.91-.94.03-.09.27-.72-.07-1.68zm-7.7-9.89h-2.4v8.15c0 1.73-.08 3.31-.25 3.79-.3.83-.94.82-1.25.66-.32-.17-.48-.41-.66-.76-.05-.09-.08-.15-.21-.24l-1.94 1.2c.32.66.79 1.23 1.4 1.6 1.27.77 3.05.36 3.64-1.46.37-.72.29-1.6.29-2.57z" fill="#000"/>
          </svg>
        );
      default:
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
          </svg>
        );
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="recent-files">
      <div className="section-header">
        <div className="section-title-with-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
          <h2>Recent Files</h2>
        </div>
        <button 
          className="refresh-btn"
          onClick={fetchRecentFiles}
          disabled={isLoading}
          title="Refresh recent files"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={isLoading ? 'spinning' : ''}>
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="m3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
        </button>
      </div>

      <div className="recent-files-content">
        {isLoading ? (
          <div className="loading-grid">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="file-card-skeleton">
                <div className="skeleton-line title"></div>
                <div className="skeleton-line"></div>
                <div className="skeleton-line short"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="error-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            <p>{error}</p>
            <button onClick={fetchRecentFiles} className="retry-btn">
              Retry
            </button>
          </div>
        ) : recentFiles.length > 0 ? (
          <div className="files-grid">
            {recentFiles.map((file) => (
              <div 
                key={file.file_id} 
                className="file-card"
                onClick={() => handleFileClick(file)}
              >
                <div className="file-header">
                  <div className="file-icon">
                    {getFileIcon(file.filename)}
                  </div>
                  <div className="file-type-badge">
                    {file.language}
                  </div>
                </div>
                <div className="file-info">
                  <h3 className="file-name" title={file.filename}>
                    {file.filename}
                  </h3>
                  <div className="file-meta">
                    <span className="file-size">{formatFileSize(file.file_size)}</span>
                    <span className="file-date">{formatDate(file.upload_time)}</span>
                  </div>
                  <div className="file-type-info">
                    {file.file_type === 'uploaded' ? 'Source' : 'Generated'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
            <h3>No Files Yet</h3>
            <p>Upload your first code file to see it appear here</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentFiles; 