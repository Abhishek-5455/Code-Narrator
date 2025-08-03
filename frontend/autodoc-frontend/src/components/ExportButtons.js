import React from 'react';
import './ExportButtons.css';

const ExportButtons = ({ generatedDocs, filename, disabled }) => {
  const exportAsMarkdown = () => {
    if (!generatedDocs) return;
    
    const blob = new Blob([generatedDocs], { type: 'text/markdown' });
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
    if (!generatedDocs) return;
    
    // Convert markdown to basic HTML
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
${generatedDocs.replace(/\n/g, '<br>')}
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

  const exportAsPDF = () => {
    if (!generatedDocs) return;
    
    // For PDF export, we'll simulate the action for now
    // In a real implementation, you might use a library like jsPDF or send to backend
    alert('PDF export feature would be implemented here. For now, you can export as HTML and then print to PDF from your browser.');
  };

  return (
    <div className="export-buttons">
      <div className="export-header">
        <span className="export-label">Export as</span>
      </div>
      
      <div className="export-button-group">
        <button 
          className={`export-btn markdown ${disabled ? 'disabled' : ''}`}
          onClick={exportAsMarkdown}
          disabled={disabled}
          title="Export as Markdown file"
        >
          Markdown
        </button>
        
        <button 
          className={`export-btn html ${disabled ? 'disabled' : ''}`}
          onClick={exportAsHTML}
          disabled={disabled}
          title="Export as HTML file"
        >
          HTML
        </button>
        
        <button 
          className={`export-btn pdf ${disabled ? 'disabled' : ''}`}
          onClick={exportAsPDF}
          disabled={disabled}
          title="Export as PDF file"
        >
          PDF
        </button>
      </div>
      
      {disabled && (
        <div className="export-hint">
          Upload a file to enable export options
        </div>
      )}
    </div>
  );
};

export default ExportButtons; 