import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, Activity, Brain, AlertTriangle, FileSearch, BarChart2 } from 'lucide-react';
import AnalyticsDashboard from './AnalyticsDashboard';
import AnalyticsHistory from './AnalyticsHistory';

function App() {
   const [file, setFile] = useState(null);
   const [isDragging, setIsDragging] = useState(false);
   const [loading, setLoading] = useState(false);
   const [result, setResult] = useState(null);
   const [error, setError] = useState(null);
   const [view, setView] = useState('analyzer'); // 'analyzer' or 'history'
   const fileInputRef = useRef(null);

   const handleDragOver = (e) => {
      e.preventDefault();
      setIsDragging(true);
   };

   const handleDragLeave = () => {
      setIsDragging(false);
   };

   const handleDrop = (e) => {
      e.preventDefault();
      setIsDragging(false);
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
         const droppedFile = e.dataTransfer.files[0];
         if (droppedFile.type === 'application/pdf') {
            setFile(droppedFile);
            setError(null);
         } else {
            setError("Please upload a PDF file.");
         }
      }
   };

   const handleFileSelect = (e) => {
      if (e.target.files && e.target.files[0]) {
         const selected = e.target.files[0];
         if (selected.type === 'application/pdf') {
            setFile(selected);
            setError(null);
         } else {
            setError("Please upload a PDF file.");
         }
      }
   };

   const handleAnalysis = async () => {
      if (!file) return;

      setLoading(true);
      setError(null);
      setResult(null);

      const formData = new FormData();
      formData.append('file', file);

      try {
         const response = await fetch('/analyze-pdf', {
            method: 'POST',
            body: formData,
         });

         if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
         }

         const data = await response.json();
         setResult(data);
      } catch (err) {
         setError(err.message);
      } finally {
         setLoading(false);
      }
   };

   // Show analytics history view
   if (view === 'history') {
      return <AnalyticsHistory onBack={() => setView('analyzer')} />;
   }

   return (
      <div style={{ minHeight: '100vh', padding: '40px 20px' }}>
         <div style={{ maxWidth: '900px', margin: '0 auto' }}>

            {/* Header */}
            <header style={{ marginBottom: '48px' }}>
               <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                     <Brain size={32} color="#2563eb" strokeWidth={2} />
                     <h1 style={{ fontSize: '28px', fontWeight: '600', margin: 0 }}>
                        PDF Analyzer
                     </h1>
                  </div>
                  <button
                     onClick={() => setView('history')}
                     style={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        border: 'none',
                        padding: '10px 20px',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '14px',
                        fontWeight: '500',
                        transition: 'all 0.2s ease'
                     }}
                  >
                     <BarChart2 size={18} />
                     Analytics
                  </button>
               </div>
               <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '14px' }}>
                  Multi-agent document intelligence system
               </p>
            </header>

            {/* Upload Section */}
            <div className="card" style={{ padding: '32px', marginBottom: '24px' }}>
               <h2 style={{ fontSize: '18px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Upload size={20} />
                  Upload Document
               </h2>

               <div
                  className={`upload-zone ${isDragging ? 'active' : ''}`}
                  style={{
                     padding: '48px 24px',
                     display: 'flex',
                     flexDirection: 'column',
                     alignItems: 'center',
                     justifyContent: 'center',
                     textAlign: 'center',
                     cursor: 'pointer',
                     marginBottom: '20px'
                  }}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current.click()}
               >
                  <FileText size={40} color={file ? '#2563eb' : '#94a3b8'} style={{ marginBottom: '12px' }} />
                  <input
                     type="file"
                     ref={fileInputRef}
                     style={{ display: 'none' }}
                     accept=".pdf"
                     onChange={handleFileSelect}
                  />
                  {file ? (
                     <div>
                        <p style={{ fontWeight: '500', margin: '0 0 4px 0' }}>{file.name}</p>
                        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
                           {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                     </div>
                  ) : (
                     <div>
                        <p style={{ margin: '0 0 4px 0' }}>Click or drag PDF here</p>
                        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>PDF files only</p>
                     </div>
                  )}
               </div>

               {error && (
                  <div style={{
                     padding: '12px',
                     background: '#fef2f2',
                     border: '1px solid #fecaca',
                     borderRadius: '6px',
                     display: 'flex',
                     alignItems: 'center',
                     gap: '8px',
                     marginBottom: '20px',
                     fontSize: '14px',
                     color: '#991b1b'
                  }}>
                     <AlertTriangle size={16} />
                     {error}
                  </div>
               )}

               <button
                  onClick={handleAnalysis}
                  disabled={!file || loading}
                  className="primary-btn"
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
               >
                  {loading ? (
                     <>
                        <Activity size={18} style={{ animation: 'spin 1s linear infinite' }} />
                        Analyzing...
                     </>
                  ) : (
                     <>
                        <FileSearch size={18} />
                        Analyze Document
                     </>
                  )}
               </button>
            </div>

            {/* Results Section */}
            {loading && (
               <div className="card" style={{ padding: '64px 32px', textAlign: 'center' }}>
                  <div style={{
                     width: '48px',
                     height: '48px',
                     border: '3px solid #e2e8f0',
                     borderTopColor: '#2563eb',
                     borderRadius: '50%',
                     margin: '0 auto 16px',
                     animation: 'spin 0.8s linear infinite'
                  }} />
                  <p style={{ color: 'var(--text-muted)', margin: 0 }}>Processing document...</p>
               </div>
            )}

            {result && (
               <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

                  {/* Document Type */}
                  <div className="card" style={{ padding: '24px' }}>
                     <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        Document Type
                     </div>
                     <div style={{ fontSize: '24px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {result.document_type}
                        <CheckCircle size={20} color="#10b981" />
                     </div>
                  </div>

                  {/* Summary */}
                  <div className="card" style={{ padding: '24px' }}>
                     <h3 style={{ fontSize: '16px', marginBottom: '16px', fontWeight: '600' }}>
                        Summary
                     </h3>
                     <p style={{ margin: 0, lineHeight: '1.7', color: 'var(--text-main)' }}>
                        {result.summary}
                     </p>
                  </div>

                  {/* Key Sections */}
                  {Object.keys(result.key_sections).length > 0 && (
                     <div className="card" style={{ padding: '24px' }}>
                        <h3 style={{ fontSize: '16px', marginBottom: '16px', fontWeight: '600' }}>
                           Key Sections
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                           {Object.entries(result.key_sections).map(([key, value], idx) => (
                              <div key={idx} style={{
                                 padding: '16px',
                                 background: 'var(--bg)',
                                 borderRadius: '6px',
                                 border: '1px solid var(--border)'
                              }}>
                                 <div style={{ fontWeight: '500', marginBottom: '6px', fontSize: '14px' }}>{key}</div>
                                 <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                                    {typeof value === 'string' ? value : JSON.stringify(value)}
                                 </div>
                              </div>
                           ))}
                        </div>
                     </div>
                  )}

                  {/* Insights */}
                  {result.insights.length > 0 && (
                     <div className="card" style={{ padding: '24px' }}>
                        <h3 style={{ fontSize: '16px', marginBottom: '16px', fontWeight: '600' }}>
                           Insights
                        </h3>
                        <ul style={{ margin: 0, padding: '0 0 0 20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                           {result.insights.map((insight, idx) => (
                              <li key={idx} style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--text-main)' }}>
                                 {insight}
                              </li>
                           ))}
                        </ul>
                     </div>
                  )}

                  {/* Agent Trace */}
                  <details className="card" style={{ padding: '24px' }}>
                     <summary style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer', color: 'var(--text-muted)' }}>
                        Agent Execution Trace
                     </summary>
                     <div style={{ marginTop: '16px', fontSize: '12px', fontFamily: 'monospace', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {result.agent_trace.map((log, idx) => (
                           <div key={idx} style={{ color: 'var(--text-muted)' }}>
                              [{idx + 1}] {log}
                           </div>
                        ))}
                     </div>
                  </details>

                  {/* Analytics Dashboard */}
                  <AnalyticsDashboard analytics={result.analytics} />

               </div>
            )}

            {!result && !loading && (
               <div className="card" style={{ padding: '64px 32px', textAlign: 'center' }}>
                  <Brain size={64} color="#e2e8f0" style={{ margin: '0 auto 16px' }} />
                  <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                     Upload a PDF to start analysis
                  </p>
               </div>
            )}

         </div>

         <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
      </div>
   )
}

export default App
