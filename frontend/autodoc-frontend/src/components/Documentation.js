import React from 'react';
import './Documentation.css';

const Documentation = ({ content, language, filename, isLoading }) => {
  const formatContent = (text) => {
    if (!text) return '';
    
    // Convert markdown-like content to HTML with syntax highlighting
    return text
      .replace(/^# (.*$)/gm, '<h1 class="doc-h1">$1</h1>')
      .replace(/^## (.*$)/gm, '<h2 class="doc-h2">$1</h2>')
      .replace(/^### (.*$)/gm, '<h3 class="doc-h3">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="doc-strong">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="doc-em">$1</em>')
      .replace(/`(.*?)`/g, '<code class="doc-code">$1</code>')
      .replace(/^- (.*$)/gm, '<div class="doc-list-item">• $1</div>')
      .replace(/\n/g, '<br />');
  };

  const exportAsMarkdown = () => {
    if (!content) return;
    
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename?.split('.')[0] || 'documentation'}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportAsHTML = () => {
    if (!content) return;
    
    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation - ${filename || 'Code'}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { color: #2c3e50; }
        code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: 'Courier New', monospace; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
${content.replace(/\n/g, '<br>')}
</body>
</html>`;
    
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename?.split('.')[0] || 'documentation'}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getDefaultContent = () => {
    return `
      <div class="default-content">
        <div class="default-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
          </svg>
        </div>
        <h3>No Documentation Yet</h3>
        <p>Upload a code file to generate documentation automatically</p>
      </div>
    `;
  };

  return (
    <div className="documentation">
      <div className="section-header">
        <div className="section-title-with-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
          </svg>
          <h2>Documentation</h2>
        </div>
        {language && (
          <div className="language-badge">
            {language}
          </div>
        )}
      </div>
      
      <div className="documentation-content">
        {isLoading ? (
          <div className="loading-skeleton">
            <div className="skeleton-line title"></div>
            <div className="skeleton-line"></div>
            <div className="skeleton-line short"></div>
            <div className="skeleton-line"></div>
            <div className="skeleton-line medium"></div>
          </div>
        ) : (
          <div 
            className="documentation-text"
            dangerouslySetInnerHTML={{ 
              __html: content ? formatContent(content) : getDefaultContent()
            }}
          />
        )}
      </div>

      <div className="export-buttons">
        <button 
          className={`export-btn markdown ${!content ? 'disabled' : ''}`}
          onClick={exportAsMarkdown}
          disabled={!content}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          </svg>
          Markdown
        </button>
        
        <button 
          className={`export-btn html ${!content ? 'disabled' : ''}`}
          onClick={exportAsHTML}
          disabled={!content}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
          HTML
        </button>
      </div>
    </div>
  );
};

export default Documentation; 