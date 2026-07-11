import React from 'react';
import { reportAPI } from '../services/api';
import { FileText, FileSpreadsheet, Download, ShieldCheck, HelpCircle } from 'lucide-react';

const Reports = ({ activeAppId }) => {

  const handleDownloadPDF = () => {
    if (!activeAppId) return;
    const url = reportAPI.getPDFUrl(activeAppId);
    window.open(url, '_blank');
  };

  const handleDownloadCSV = () => {
    if (!activeAppId) return;
    const url = reportAPI.getCSVUrl(activeAppId);
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6 max-w-4xl">
      
      <div>
        <h1 className="font-bold text-2xl text-slate-100">Executive & Technical Report Center</h1>
        <p className="text-xs text-slate-400 mt-1">Download compliance reports and technical remediation patchlists in PDF and CSV format.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* PDF Executive Report Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-6 flex flex-col justify-between shadow-lg space-y-4">
          <div className="space-y-2">
            <div className="bg-indigo-500/10 p-3 rounded-lg text-indigo-500 w-fit">
              <FileText size={28} />
            </div>
            <h3 className="font-bold text-base text-slate-200">Executive Risk Summary PDF</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Generate a corporate executive compliance summary. This includes risk severity ratings, top active CVE vulnerabilities tables, copyleft compliance audits, and priority advisor action checklists.
            </p>
          </div>
          
          <button 
            onClick={handleDownloadPDF}
            className="w-full py-2.5 bg-indigo-650 hover:bg-indigo-755 text-white font-semibold rounded-lg text-sm transition-colors flex items-center justify-center gap-2 shadow"
          >
            <Download size={16} />
            <span>Generate Executive PDF</span>
          </button>
        </div>

        {/* CSV Developer Report Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-6 flex flex-col justify-between shadow-lg space-y-4">
          <div className="space-y-2">
            <div className="bg-emerald-500/10 p-3 rounded-lg text-emerald-500 w-fit">
              <FileSpreadsheet size={28} />
            </div>
            <h3 className="font-bold text-base text-slate-200">Developer Patching Manifest CSV</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Export a technical developer spreadsheet. It maps libraries, versions, CVE IDs, CVSS scores, patched versions, and the direct commands required to install updates.
            </p>
          </div>
          
          <button 
            onClick={handleDownloadCSV}
            className="w-full py-2.5 bg-emerald-650 hover:bg-emerald-755 text-white font-semibold rounded-lg text-sm transition-colors flex items-center justify-center gap-2 shadow"
          >
            <Download size={16} />
            <span>Download Developers CSV</span>
          </button>
        </div>

      </div>

      {/* Compliance Checklist section */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 shadow">
        <h3 className="font-bold text-sm text-slate-200 mb-4 flex items-center gap-1.5">
          <ShieldCheck size={16} className="text-indigo-500" />
          Enterprise Compliance Status Checklists
        </h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs leading-normal">
          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-cyber-darker/40 border border-cyber-border">
            <div className="w-5 h-5 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center font-bold">✓</div>
            <span>No restrictive copyleft linking dependencies detected.</span>
          </div>
          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-cyber-darker/40 border border-cyber-border">
            <div className="w-5 h-5 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center font-bold">✓</div>
            <span>All software manifest files satisfy CycloneDX schema schemas.</span>
          </div>
          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-cyber-darker/40 border border-cyber-border">
            <div className="w-5 h-5 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center font-bold">✓</div>
            <span>Vulnerability timeline metrics matched with CVE databases.</span>
          </div>
          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-cyber-darker/40 border border-cyber-border">
            <div className="w-5 h-5 rounded-full bg-amber-500/10 text-amber-500 flex items-center justify-center font-bold">!</div>
            <span className="text-slate-350">Certain libraries lack active maintainers. Check Maintenance Dashboard.</span>
          </div>
        </div>
      </div>

    </div>
  );
};

export default Reports;
