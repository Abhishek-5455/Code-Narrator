import React, { useRef, useState } from 'react';
import axios from 'axios';
import './CodeUpload.css';

const CodeUpload = ({ onFileUpload, onLoading, isLoading }) => {
  const fileInputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');

  const API_BASE_URL = 'http://localhost:8000';

  const handleFiles = async (files) => {
    if (files && files.length > 0) {
      const file = files[0];
      setError('');
      onLoading(true);

      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(`${API_BASE_URL}/parse-code/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.error) {
          setError(response.data.message || 'Error processing file');
        } else {
          onFileUpload(file, response.data.markdown_content, response.data.language);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        
        if (error.code === 'ERR_NETWORK') {
          setError('Cannot connect to server. Please ensure the backend server is running on http://localhost:8000');
        } else if (error.response) {
          setError(`Server error: ${error.response.data?.message || error.response.statusText}`);
        } else if (error.request) {
          setError('No response from server. Please check if the backend is running and CORS is configured.');
        } else {
          setError(`Upload failed: ${error.message}`);
        }
      } finally {
        onLoading(false);
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="code-upload-horizontal">
      <div
        className={`upload-area-horizontal ${dragActive ? 'drag-active' : ''} ${isLoading ? 'loading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="file-input"
          accept=".py,.java,.js,.jsx"
          onChange={handleChange}
        />
        
        <div className="upload-content-horizontal">
          {isLoading ? (
            <div className="loading-content">
              <div className="spinner-small"></div>
              <span>Processing your file...</span>
            </div>
          ) : (
            <>
              <div className="upload-icon-horizontal">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7,10 12,15 17,10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
              </div>
              <div className="upload-text-content">
                <h3 className="upload-title">Drag & drop your code files here</h3>
                <p className="upload-subtitle">
                  Or <span className="upload-link">browse files</span> to get started
                </p>
                <div className="supported-types">
                  <span className="file-type">Python</span>
                  <span className="file-type">Java</span>
                  <span className="file-type">JavaScript</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
      
      {error && (
        <div className="error-message-horizontal">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f44336" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default CodeUpload; 