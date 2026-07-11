import React, { useState, useEffect } from 'react';
import { licenseAPI } from '../services/api';
import { Scale, CheckCircle, AlertOctagon, Info, HelpCircle, ShieldAlert } from 'lucide-react';

const LicenseDashboard = ({ activeAppId }) => {
  const [licenseData, setLicenseData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLicenses = async () => {
      if (!activeAppId) return;
      setLoading(true);
      try {
        const res = await licenseAPI.auditApplication(activeAppId);
        setLicenseData(res.data.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadLicenses();
  }, [activeAppId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-indigo-650/30 border-t-indigo-600 animate-spin"></div>
        <p className="text-sm text-slate-400">Auditing codebase licensing compliance...</p>
      </div>
    );
  }

  const score = licenseData?.license_score || 100;
  const conflicts = licenseData?.conflicts || [];
  const warnings = licenseData?.warnings || [];
  const recommendations = licenseData?.recommendations || [];

  return (
    <div className="space-y-6">
      
      <div>
        <h1 className="font-bold text-2xl text-slate-100">License Compliance Auditing</h1>
        <p className="text-xs text-slate-400 mt-1">Audit dependency components licenses against standard legal guidelines and compliance matrices.</p>
      </div>

      {/* Score and Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Score Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex flex-col items-center justify-center space-y-4 text-center shadow-lg">
          <h3 className="font-bold text-sm text-slate-205">Compliance Audit Score</h3>
          <div className="w-32 h-32 rounded-full border-8 border-indigo-600 flex flex-col items-center justify-center bg-indigo-950/10">
            <span className="text-4xl font-black text-slate-100">{score}</span>
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider mt-0.5">Score</span>
          </div>
          <p className="text-xs text-slate-400">Penalty reductions reflect strong copyleft or unidentified packages.</p>
        </div>

        {/* Counter cards */}
        <div className="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow">
            <div className="space-y-1">
              <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">GPL Copyleft Conflicts</span>
              <p className="text-3xl font-extrabold text-red-500">{licenseData?.conflicts_count}</p>
            </div>
            <div className="bg-red-500/10 p-3 rounded-lg text-red-500">
              <AlertOctagon size={24} />
            </div>
          </div>

          <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow">
            <div className="space-y-1">
              <span className="text-xs text-slate-455 uppercase font-bold tracking-wider">Unidentified Warnings</span>
              <p className="text-3xl font-extrabold text-amber-500">{licenseData?.warnings_count}</p>
            </div>
            <div className="bg-amber-500/10 p-3 rounded-lg text-amber-500">
              <HelpCircle size={24} />
            </div>
          </div>

          <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 sm:col-span-2 flex flex-col justify-start space-y-3">
            <h4 className="font-bold text-xs text-slate-200 uppercase tracking-wide">Developer Licensing Action Plans</h4>
            <div className="space-y-1.5 max-h-32 overflow-y-auto text-xs leading-normal">
              {recommendations.map((rec, idx) => (
                <p key={idx} className="text-slate-350 bg-slate-900 px-3 py-2 rounded border border-cyber-border flex items-start gap-1.5">
                  <span className="font-bold text-indigo-400">Remediation:</span>
                  <span>{rec}</span>
                </p>
              ))}
              {recommendations.length === 0 && (
                <p className="text-slate-450 text-center py-4">No active remediation actions required. Codebase complies with commercial policies.</p>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* Grid: Details tabs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Conflicts Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5">
          <h3 className="font-bold text-sm text-red-500 mb-4 flex items-center gap-1.5">
            <AlertOctagon size={16} />
            Strong Copyleft Violations ({conflicts.length})
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto text-xs leading-normal">
            {conflicts.map((c, idx) => (
              <div key={idx} className="p-3 bg-red-500/5 rounded border border-red-500/10 space-y-1.5">
                <div className="flex justify-between font-bold text-slate-200">
                  <span>Library: {c.library_name} @{c.library_version}</span>
                  <span className="text-red-400 uppercase tracking-wide font-mono text-[10px]">{c.license_name}</span>
                </div>
                <p className="text-slate-400">{c.description}</p>
              </div>
            ))}
            {conflicts.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                No copyleft license violations detected.
              </div>
            )}
          </div>
        </div>

        {/* Warnings Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5">
          <h3 className="font-bold text-sm text-amber-500 mb-4 flex items-center gap-1.5">
            <HelpCircle size={16} />
            Unclassified & Unknown Licenses ({warnings.length})
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto text-xs leading-normal">
            {warnings.map((w, idx) => (
              <div key={idx} className="p-3 bg-amber-500/5 rounded border border-amber-500/10 space-y-1.5">
                <div className="flex justify-between font-bold text-slate-200">
                  <span>Library: {w.library_name} @{w.library_version}</span>
                  <span className="text-amber-400 font-mono uppercase text-[10px]">{w.license_name}</span>
                </div>
                <p className="text-slate-400">{w.description}</p>
              </div>
            ))}
            {warnings.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                All dependency licenses successfully resolved.
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};

export default LicenseDashboard;
