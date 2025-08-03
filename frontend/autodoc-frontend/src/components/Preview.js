import React from 'react';
import './Preview.css';

const Preview = ({ content, language, isLoading }) => {
  const formatContent = (text) => {
    if (!text) return '';
    
    // Convert markdown-like content to simple HTML
    return text
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br />');
  };

  const getDefaultPreviewContent = () => {
    return `
      <h2>class MyClass:</h2>
      <p style="color: #888; margin: 8px 0;">A simple example class.</p>
      
      <div style="margin: 16px 0;">
        <strong>def __init__(self, value: int) -> None</strong><br/>
        <span style="color: #888; margin-left: 20px;">Initialize the class<br/>with a value.</span>
      </div>
      
      <div style="margin: 16px 0;">
        <strong>def get_value(self) -> int:</strong><br/>
        <span style="color: #888; margin-left: 20px;">Return the value.</span>
      </div>
      
      <div style="margin: 16px 0;">
        <strong>def get_value(self) -> int</strong><br/>
        <span style="color: #888; margin-left: 20px;">Return the value.</span>
      </div>
    `;
  };

  return (
    <div className="preview">
      <h2 className="section-title">Preview</h2>
      
      <div className="preview-content">
        {isLoading ? (
          <div className="loading-preview">
            <div className="skeleton-lines">
              <div className="skeleton-line skeleton-title"></div>
              <div className="skeleton-line skeleton-text"></div>
              <div className="skeleton-line skeleton-text short"></div>
              <div className="skeleton-line skeleton-text"></div>
              <div className="skeleton-line skeleton-text medium"></div>
            </div>
          </div>
        ) : (
          <div 
            className="preview-text"
            dangerouslySetInnerHTML={{ 
              __html: content ? formatContent(content) : getDefaultPreviewContent()
            }}
          />
        )}
      </div>
      
      {language && !isLoading && (
        <div className="language-badge">
          <span>{language}</span>
        </div>
      )}
    </div>
  );
};

export default Preview; 