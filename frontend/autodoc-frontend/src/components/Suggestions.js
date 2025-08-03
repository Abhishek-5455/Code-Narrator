import React from 'react';
import './Suggestions.css';

const Suggestions = ({ suggestions, language, isLoading }) => {
  const getSuggestionIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'warning':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffa726" strokeWidth="2">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        );
      case 'error':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f44336" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        );
      case 'info':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2196f3" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
        );
      default:
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4caf50" strokeWidth="2">
            <path d="M9 12l2 2 4-4"></path>
            <circle cx="12" cy="12" r="10"></circle>
          </svg>
        );
    }
  };

  const formatSuggestion = (suggestion) => {
    if (typeof suggestion === 'string') {
      return suggestion;
    }
    
    if (suggestion.message) {
      return suggestion.message;
    }
    
    return JSON.stringify(suggestion);
  };

  const getDefaultContent = () => {
    return (
      <div className="default-content">
        <div className="default-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="m9 12 2 2 4-4"></path>
          </svg>
        </div>
        <h3>No Suggestions Yet</h3>
        <p>Upload a code file to get intelligent refactoring suggestions</p>
      </div>
    );
  };

  return (
    <div className="suggestions">
      <div className="section-header">
        <div className="section-title-with-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
          <h2>Suggestions</h2>
        </div>
        {suggestions.length > 0 && (
          <div className="suggestions-count">
            {suggestions.length} {suggestions.length === 1 ? 'suggestion' : 'suggestions'}
          </div>
        )}
      </div>
      
      <div className="suggestions-content">
        {isLoading ? (
          <div className="loading-skeleton">
            <div className="skeleton-line title"></div>
            <div className="skeleton-line"></div>
            <div className="skeleton-line short"></div>
            <div className="skeleton-line"></div>
            <div className="skeleton-line medium"></div>
          </div>
        ) : suggestions.length > 0 ? (
          <div className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="suggestion-item">
                <div className="suggestion-header">
                  <div className="suggestion-icon">
                    {getSuggestionIcon(suggestion.type || 'suggestion')}
                  </div>
                  <div className="suggestion-meta">
                    {suggestion.line && (
                      <span className="suggestion-line">Line {suggestion.line}</span>
                    )}
                    {suggestion.type && (
                      <span className={`suggestion-type ${suggestion.type.toLowerCase()}`}>
                        {suggestion.type}
                      </span>
                    )}
                  </div>
                </div>
                <div className="suggestion-content">
                  <p className="suggestion-message">
                    {formatSuggestion(suggestion)}
                  </p>
                  {suggestion.code && (
                    <div className="suggestion-code">
                      <code>{suggestion.code}</code>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          getDefaultContent()
        )}
      </div>
    </div>
  );
};

export default Suggestions; 