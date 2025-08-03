import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ uploadedFile, generatedDocs }) => {
  const [coverage, setCoverage] = useState(75); // Default coverage from design
  const [stats, setStats] = useState({
    totalFunctions: 0,
    documentedFunctions: 0,
    totalClasses: 0,
    documentedClasses: 0
  });

  useEffect(() => {
    if (generatedDocs) {
      calculateCoverage(generatedDocs);
    }
  }, [generatedDocs]);

  const calculateCoverage = (docs) => {
    // Simple coverage calculation based on documentation content
    const functions = (docs.match(/def\s+\w+/g) || []).length;
    const classes = (docs.match(/class\s+\w+/g) || []).length;
    const docstrings = (docs.match(/Docstring:/g) || []).length;
    
    const totalItems = functions + classes;
    const documentedItems = Math.min(docstrings, totalItems);
    
    const calculatedCoverage = totalItems > 0 ? Math.round((documentedItems / totalItems) * 100) : 75;
    
    setCoverage(calculatedCoverage);
    setStats({
      totalFunctions: functions,
      documentedFunctions: Math.min(docstrings, functions),
      totalClasses: classes,
      documentedClasses: Math.min(docstrings, classes)
    });
  };

  return (
    <div className="dashboard">
      <h2 className="section-title">Dashboard</h2>
      
      <div className="dashboard-content">
        <div className="coverage-section">
          <h3 className="coverage-title">Documentation Coverage</h3>
          
          <div className="coverage-display">
            <div className="coverage-percentage">{coverage}%</div>
            <div className="coverage-bar">
              <div 
                className="coverage-fill"
                style={{ width: `${coverage}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        {uploadedFile && (
          <div className="file-info">
            <div className="info-item">
              <span className="info-label">File:</span>
              <span className="info-value">{uploadedFile.name}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Size:</span>
              <span className="info-value">{(uploadedFile.size / 1024).toFixed(1)} KB</span>
            </div>
          </div>
        )}
        
        {generatedDocs && (
          <div className="stats-section">
            <div className="stat-item">
              <span className="stat-number">{stats.totalFunctions}</span>
              <span className="stat-label">Functions</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.totalClasses}</span>
              <span className="stat-label">Classes</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.documentedFunctions + stats.documentedClasses}</span>
              <span className="stat-label">Documented</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 