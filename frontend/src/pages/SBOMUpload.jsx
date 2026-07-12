import React, { useState, useEffect } from 'react';
import { sbomAPI, dashboardAPI } from '../services/api';
import { UploadCloud, CheckCircle, AlertOctagon, RefreshCw, FileText, ChevronRight } from 'lucide-react';

const SBOMUpload = () => {
  const [apps, setApps] = useState([]);
  const [selectedAppId, setSelectedAppId] = useState('');
  const [file, setFile] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(''); // 'staged', 'parsing', 'completed', 'failed'
  const [uploadId, setUploadId] = useState(null);
  const [report, setReport] = useState(null);
  const [errorDetails, setErrorDetails] = useState(null);

  useEffect(() => {
    const loadApps = async () => {
      try {
        const res = await dashboardAPI.getSummary();
        const appsList = res.data.data.applications_status || [];
        setApps(appsList);
        if (appsList.length > 0) {
          setSelectedAppId(appsList[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    loadApps();
  }, []);

  // Reset the audit log whenever the user picks a different application
  const handleAppChange = (e) => {
    setSelectedAppId(e.target.value);
    setFile(null);
    setStatus('');
    setReport(null);
    setErrorDetails(null);
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus('');
      setReport(null);
      setErrorDetails(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
      setStatus('');
      setReport(null);
      setErrorDetails(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleUploadAndIngest = async () => {
    if (!selectedAppId || !file) {
      alert("Please select a target application and an SBOM file.");
      return;
    }

    setLoading(true);
    setStatus('staging');
    
    try {
      // 1. Stage upload file
      const uploadRes = await sbomAPI.uploadSBOM(selectedAppId, file);
      const stageData = uploadRes.data.data;
      setUploadId(stageData.upload_id);
      setStatus('staged');
      
      // 2. Automatically trigger ingestion parsing pipeline
      setStatus('parsing');
      const parseRes = await sbomAPI.parseSBOM(stageData.upload_id);
      // Store the full parseData so both libraries_imported AND validation_report are accessible
      const parseData = parseRes.data.data;
      setReport(parseData);
      setStatus('completed');
    } catch (err) {
      console.error("Ingestion failed:", err);
      const errorObj = err.response?.data?.error || {};
      const details = errorObj.details || {};
      const message = errorObj.message || "Internal Ingestion Parser Error.";
      // A structural validation FAILED parse returns errors inside details.errors
      // A duplicate returns the message directly
      const isDuplicate = message.toLowerCase().includes("already processed");
      if (isDuplicate) {
        setStatus('duplicate');
        setErrorDetails([message]);
      } else {
        setStatus('failed');
        // Try to extract the structural validation errors from the nested report
        const validationErrors = details.validation_report?.errors ||
                                 details.errors ||
                                 [message];
        setErrorDetails(validationErrors);
        // Also store the validation report if available so warnings are visible
        if (details.validation_report) {
          setReport(details);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="font-bold text-2xl text-slate-100">SBOM Ingestion & Auditing Center</h1>
        <p className="text-xs text-slate-400 mt-1">Upload CycloneDX JSON, SPDX JSON, or custom tabular CSV manifests to analyze software package versions.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Side: Upload Manifest Configurations Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 md:col-span-2 space-y-5">
          <h3 className="font-bold text-sm text-slate-200">Import Manifest Configurations</h3>
          
          {/* Target App selection */}
          <div>
            <label className="text-xs text-slate-400 font-bold block mb-1.5 uppercase">Select Target Application</label>
            <select 
              value={selectedAppId}
              onChange={handleAppChange}
              className="w-full bg-cyber-darker border border-cyber-border text-slate-200 text-sm px-3 py-2 rounded-lg focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 cursor-pointer"
            >
              {apps.map(app => (
                <option key={app.id} value={app.id}>{app.name} v{app.version}</option>
              ))}
            </select>
          </div>

          {/* Drag & Drop File box */}
          <div 
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="border-2 border-dashed border-slate-700 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer hover:border-indigo-500 transition-colors bg-cyber-darker/50"
            onClick={() => document.getElementById('sbom-input-file').click()}
          >
            <input 
              id="sbom-input-file"
              type="file"
              accept=".json,.csv"
              onChange={handleFileChange}
              className="hidden"
            />
            <UploadCloud size={44} className="text-indigo-500 mb-3 animate-bounce-slow" />
            <p className="text-sm font-semibold text-slate-200">Drag & Drop SBOM manifest file here</p>
            <p className="text-xs text-slate-400 mt-1">Accepts CycloneDX (.json), SPDX (.json), or Dependencies (.csv) up to 25MB</p>
            
            {file && (
              <div className="mt-4 flex items-center gap-2 px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200">
                <FileText size={14} className="text-indigo-400" />
                <span>{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
            )}
          </div>

          <button 
            onClick={handleUploadAndIngest}
            disabled={loading || !file}
            className="w-full py-2.5 bg-indigo-650 hover:bg-indigo-750 disabled:bg-indigo-650/40 text-white font-semibold rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                <span>Processing... {status === 'parsing' ? 'Auditing Vulnerabilities' : 'Staging Manifest'}</span>
              </>
            ) : (
              <span>Analyze Software Manifest</span>
            )}
          </button>
        </div>

        {/* Right Side: Parsing & Ingestion Status Log Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-4">
          <h3 className="font-bold text-sm text-slate-200">Validation Audit Log</h3>
          
          {status === '' && (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500 text-xs">
              <FileText size={32} className="mb-2" />
              <p>Upload a file to start validation.</p>
            </div>
          )}

          {/* Running progress animations */}
          {(status === 'staging' || status === 'parsing') && (
            <div className="space-y-4 py-6">
              <div className="flex justify-between text-xs text-slate-400">
                <span className="capitalize">{status} manifest...</span>
                <span>Active</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div className="bg-indigo-650 h-full w-2/3 rounded-full animate-pulse-slow"></div>
              </div>
              <p className="text-xs text-slate-450 leading-relaxed">
                Parser service is resolving dependencies hierarchy trees and matching definitions in CVE vulnerabilities databases.
              </p>
            </div>
          )}

          {/* Completed validation report */}
          {status === 'completed' && report && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-emerald-500">
                <CheckCircle size={20} />
                <span className="font-bold text-sm">Ingestion Success</span>
              </div>
              
              <div className="space-y-2 pt-2 border-t border-cyber-border text-xs text-slate-350">
                <div className="flex justify-between">
                  <span>Libraries Imported:</span>
                  <span className="font-semibold text-slate-200">
                    {report.libraries_imported ?? report.validation_report?.metrics?.libraries_count ?? 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Dependency Edges:</span>
                  <span className="font-semibold text-slate-200">
                    {report.validation_report?.metrics?.dependencies_count ?? report.metrics?.dependencies_count ?? 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Has Cycle Reference:</span>
                  <span className="font-semibold text-slate-200">
                    {(report.validation_report?.metrics?.has_cycles || report.metrics?.has_cycles) ? 'YES' : 'NO'}
                  </span>
                </div>
              </div>

              {/* Validation warnings */}
              {(report.validation_report?.warnings || report.warnings || []).length > 0 && (
                <div className="mt-4 border-t border-cyber-border pt-4">
                  <h4 className="text-xs text-amber-500 font-bold mb-2 uppercase tracking-wide">
                    Warnings ({(report.validation_report?.warnings || report.warnings || []).length})
                  </h4>
                  <ul className="space-y-1 max-h-32 overflow-y-auto text-[11px] text-slate-400 list-disc list-inside">
                    {(report.validation_report?.warnings || report.warnings || []).map((w, idx) => (
                      <li key={idx} className="leading-snug">{w}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Duplicate file warning */}
          {status === 'duplicate' && errorDetails && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-amber-400">
                <AlertOctagon size={20} />
                <span className="font-bold text-sm">Already Processed</span>
              </div>
              <div className="border-t border-cyber-border pt-3 space-y-3">
                <p className="text-[11px] text-slate-400 leading-relaxed">{errorDetails[0]}</p>
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 text-[11px] text-amber-300 leading-relaxed">
                  💡 <strong>Tip:</strong> To re-analyze, upload a new or updated version of this SBOM file, or select a different application target.
                </div>
              </div>
            </div>
          )}

          {/* Failed validation errors listing */}
          {status === 'failed' && errorDetails && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-red-500">
                <AlertOctagon size={20} />
                <span className="font-bold text-sm">Ingestion Rejected</span>
              </div>
              
              <div className="border-t border-cyber-border pt-3">
                <h4 className="text-xs text-red-400 font-bold mb-2 uppercase">Critical Structural Errors</h4>
                <ul className="space-y-1 max-h-48 overflow-y-auto text-[11px] text-slate-400 list-disc list-inside">
                  {errorDetails.map((err, idx) => (
                    <li key={idx} className="leading-snug">{err}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default SBOMUpload;
