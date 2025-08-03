import React, { useState, createContext, useContext } from 'react';
import './App.css';
import Navigation from './components/Navigation';
import CodeUpload from './components/CodeUpload';
import Documentation from './components/Documentation';
import Suggestions from './components/Suggestions';
import RecentFiles from './components/RecentFiles';

// Theme Context
const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [generatedDocs, setGeneratedDocs] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [language, setLanguage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [refreshRecentFiles, setRefreshRecentFiles] = useState(0);

  const handleFileUpload = async (file, docs, lang) => {
    setUploadedFile(file);
    setGeneratedDocs(docs);
    setLanguage(lang);
    
    // Generate suggestions for the uploaded file
    await generateSuggestions(file);
    
    // Refresh recent files list
    setRefreshRecentFiles(prev => prev + 1);
  };

  const generateSuggestions = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/suggest/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.suggestions) {
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error('Error generating suggestions:', error);
      setSuggestions([]);
    }
  };

  const handleLoading = (loading) => {
    setIsLoading(loading);
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const themeValue = {
    isDarkMode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={themeValue}>
      <div className={`App ${isDarkMode ? 'dark-theme' : 'light-theme'}`}>
        <Navigation />
        
        <main className="main-container">
          {/* File Upload Section */}
          <section className="upload-section">
            <CodeUpload 
              onFileUpload={handleFileUpload}
              onLoading={handleLoading}
              isLoading={isLoading}
            />
          </section>

          {/* Content Sections */}
          <div className="content-grid">
            <div className="documentation-section">
              <Documentation 
                content={generatedDocs}
                language={language}
                filename={uploadedFile?.name}
                isLoading={isLoading}
              />
            </div>

            <div className="suggestions-section">
              <Suggestions 
                suggestions={suggestions}
                language={language}
                isLoading={isLoading}
              />
            </div>
          </div>

          {/* Recent Files Section */}
          <section className="recent-files-section">
            <RecentFiles 
              refreshTrigger={refreshRecentFiles}
              onFileSelect={handleFileUpload}
            />
          </section>
        </main>
      </div>
    </ThemeContext.Provider>
  );
}

export default App;
