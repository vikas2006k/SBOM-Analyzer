import React, { useState, useEffect } from 'react';
import { riskAPI } from '../services/api';
import { AlertTriangle, RefreshCw, Sparkles, AlertCircle, Play } from 'lucide-react';

const RiskDashboard = ({ activeAppId }) => {
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);

  const loadRiskScore = async () => {
    if (!activeAppId) return;
    setLoading(true);
    try {
      const res = await riskAPI.getRiskReport(activeAppId);
      setRiskData(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRiskScore();
  }, [activeAppId]);

  const handleRecalculate = async () => {
    if (!activeAppId) return;
    setRecalculating(true);
    try {
      const res = await riskAPI.recalculateRisk(activeAppId);
      setRiskData(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setRecalculating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-indigo-650/30 border-t-indigo-600 animate-spin"></div>
        <p className="text-sm text-slate-400">Loading risk scores analytics...</p>
      </div>
    );
  }

  const score = riskData?.overall_score || 0.0;
  const severity = riskData?.severity || 'Low';
  
  // Scoring styling helpers
  const severityColors = {
    Critical: 'text-red-500 border-red-500 bg-red-500/10',
    High: 'text-orange-500 border-orange-500 bg-orange-500/10',
    Medium: 'text-amber-500 border-amber-500 bg-amber-500/10',
    Low: 'text-emerald-500 border-emerald-500 bg-emerald-500/10'
  };
  
  const scoreColor = severityColors[severity] || severityColors.Low;

  return (
    <div className="space-y-6">
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-bold text-2xl text-slate-100">Composite Risk Scorer Engine</h1>
          <p className="text-xs text-slate-400 mt-1">Multi-factor cybersecurity threat model analyzing CVE impact, copyleft license exposures, architecture depths, and maintenance score indexes.</p>
        </div>
        <button 
          onClick={handleRecalculate}
          disabled={recalculating}
          className="px-4 py-2 bg-indigo-655 hover:bg-indigo-750 disabled:bg-indigo-655/40 text-white font-semibold rounded-lg text-sm transition-colors flex items-center gap-2 shadow"
        >
          <RefreshCw size={16} className={recalculating ? 'animate-spin' : ''} />
          <span>Recalculate Risk</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Risk Score Circle widget */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-6 flex flex-col items-center justify-center space-y-5 text-center shadow-lg">
          <h3 className="font-bold text-sm text-slate-200">Application Threat Score</h3>
          
          {/* Outer glow ring */}
          <div className={`w-44 h-44 rounded-full border-8 flex flex-col items-center justify-center shadow-2xl relative ${scoreColor.split(' ')[1]}`}>
            <span className="text-5xl font-black tracking-tighter text-slate-150">{score}</span>
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Risk Score</span>
          </div>

          <div className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase border tracking-widest ${scoreColor}`}>
            {severity} Threat Rating
          </div>
        </div>

        {/* Dynamic Explanation block */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-6 lg:col-span-2 flex flex-col justify-between shadow-lg space-y-4">
          <div className="space-y-3">
            <h3 className="font-bold text-sm text-slate-205 flex items-center gap-1.5">
              <Sparkles size={16} className="text-indigo-500" />
              AI Risk Explanation Analyst
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              {riskData?.explanation}
            </p>
          </div>
          
          <div className="border-t border-cyber-border pt-3 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-450 uppercase font-bold tracking-wider text-[9px]">CVSS Risk</span>
              <p className="font-semibold text-slate-200 mt-0.5">{riskData?.sub_scores?.cvss_risk}/100</p>
            </div>
            <div>
              <span className="text-slate-455 uppercase font-bold tracking-wider text-[9px]">License Risk</span>
              <p className="font-semibold text-slate-200 mt-0.5">{riskData?.sub_scores?.license_risk}/100</p>
            </div>
            <div>
              <span className="text-slate-455 uppercase font-bold tracking-wider text-[9px]">Maintenance Risk</span>
              <p className="font-semibold text-slate-200 mt-0.5">{riskData?.sub_scores?.maintenance_risk}/100</p>
            </div>
            <div>
              <span className="text-slate-455 uppercase font-bold tracking-wider text-[9px]">Architecture Risk</span>
              <p className="font-semibold text-slate-200 mt-0.5">{riskData?.sub_scores?.architecture_risk}/100</p>
            </div>
          </div>
        </div>

      </div>

      {/* Grid: Risk Factors list */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-5">
        <h3 className="font-bold text-sm text-slate-200 mb-4 flex items-center gap-1.5">
          <AlertCircle size={16} className="text-indigo-500" />
          Workspace Risk Factors Audit
        </h3>

        <div className="space-y-3">
          {riskData?.factors?.map((factor, idx) => (
            <div key={idx} className="p-4 rounded-xl border border-cyber-border bg-cyber-darker/40 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs leading-normal">
              <div className="space-y-1">
                <p className="font-bold text-slate-200 text-sm">Factor: {factor.type}</p>
                <p className="text-slate-400">{factor.description}</p>
              </div>
              <span className={`px-3 py-1 rounded-full font-bold uppercase tracking-widest text-[9px] text-center border shrink-0 ${
                factor.impact === 'Critical' 
                  ? 'bg-red-500/10 text-red-500 border-red-500/20' 
                  : factor.impact === 'High' 
                    ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' 
                    : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
              }`}>
                {factor.impact} Impact
              </span>
            </div>
          ))}
          {!riskData?.factors?.length && (
            <p className="text-xs text-slate-400 py-6 text-center">No active risk factors logged. Project codebase health satisfies policies rules.</p>
          )}
        </div>
      </div>

    </div>
  );
};

export default RiskDashboard;
