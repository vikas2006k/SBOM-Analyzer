import React, { useState, useEffect } from 'react';
import { maintenanceAPI } from '../services/api';
import { Wrench, CheckCircle, AlertTriangle, AlertCircle, Calendar, UserCheck } from 'lucide-react';

const MaintenanceDashboard = ({ activeAppId }) => {
  const [maintData, setMaintData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadMaintenance = async () => {
      if (!activeAppId) return;
      setLoading(true);
      try {
        const res = await maintenanceAPI.auditApplication(activeAppId);
        setMaintData(res.data.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadMaintenance();
  }, [activeAppId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-indigo-650/30 border-t-indigo-600 animate-spin"></div>
        <p className="text-sm text-slate-400">Auditing codebase maintainability indexes...</p>
      </div>
    );
  }

  const score = maintData?.average_maintenance_score || 100;
  const deprecated = maintData?.deprecated_count || 0;
  const abandoned = maintData?.abandoned_count || 0;
  const list = maintData?.dependencies || [];

  return (
    <div className="space-y-6">
      
      <div>
        <h1 className="font-bold text-2xl text-slate-100">Open-Source Maintenance & Health Index</h1>
        <p className="text-xs text-slate-400 mt-1">Audit dependency project updates, commit frequencies, deprecations, and dev sustainability risks.</p>
      </div>

      {/* KPI Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow">
          <div className="space-y-1">
            <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">Average Health Score</span>
            <p className="text-3xl font-extrabold text-slate-200">{score}/100</p>
          </div>
          <div className="bg-indigo-500/10 p-3 rounded-lg text-indigo-500">
            <Wrench size={24} />
          </div>
        </div>

        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow">
          <div className="space-y-1">
            <span className="text-xs text-slate-455 uppercase font-bold tracking-wider">Deprecated Packages</span>
            <p className="text-3xl font-extrabold text-red-500">{deprecated}</p>
          </div>
          <div className="bg-red-500/10 p-3 rounded-lg text-red-500">
            <AlertCircle size={24} />
          </div>
        </div>

        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow">
          <div className="space-y-1">
            <span className="text-xs text-slate-455 uppercase font-bold tracking-wider">Stale / Abandoned</span>
            <p className="text-3xl font-extrabold text-orange-500">{abandoned}</p>
          </div>
          <div className="bg-orange-500/10 p-3 rounded-lg text-orange-500">
            <Calendar size={24} />
          </div>
        </div>
      </div>

      {/* Dependencies Maintenance Audit list */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-5">
        <h3 className="font-bold text-sm text-slate-200 mb-4 flex items-center gap-1.5">
          <Wrench size={16} className="text-indigo-500" />
          Libraries Project Sustainability Audit
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-cyber-border text-slate-400 text-xs uppercase tracking-wider">
                <th className="py-3 px-4">Package</th>
                <th className="py-3 px-4">Last Release Date</th>
                <th className="py-3 px-4">Annual Commits</th>
                <th className="py-3 px-4">Bus Factor</th>
                <th className="py-3 px-4">Health Index</th>
                <th className="py-3 px-4 text-right">Warnings</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border">
              {list.map(lib => (
                <tr key={lib.library_id} className="hover:bg-slate-800/20 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-slate-200">
                    {lib.library_name} <span className="text-xs text-slate-500">v{lib.library_version}</span>
                    {lib.is_deprecated && (
                      <span className="bg-red-500/10 border border-red-500/20 text-red-400 text-[9px] font-bold px-1.5 py-0.5 rounded ml-2">
                        Deprecated
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-slate-350">
                    {new Date(lib.last_release).toLocaleDateString()}
                    <span className="text-xs text-slate-550 block mt-0.5">({lib.age_days} days ago)</span>
                  </td>
                  <td className="py-3.5 px-4 font-semibold text-slate-200">{lib.commit_frequency_annual} commits</td>
                  <td className="py-3.5 px-4 font-semibold text-slate-200">
                    <span className="inline-flex items-center gap-1">
                      <UserCheck size={12} className={lib.bus_factor <= 1 ? 'text-red-400' : 'text-slate-400'} />
                      {lib.bus_factor} dev{lib.bus_factor > 1 && 's'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      lib.health_level === 'Healthy' 
                        ? 'bg-emerald-500/10 text-emerald-500' 
                        : lib.health_level === 'Medium Risk' 
                          ? 'bg-amber-500/10 text-amber-500' 
                          : 'bg-red-500/10 text-red-500'
                    }`}>
                      {lib.maintenance_score}/100
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    {lib.warnings?.length > 0 ? (
                      <span className="text-red-400 inline-flex items-center gap-0.5 font-bold hover:underline cursor-pointer" title={lib.warnings.join(', ')}>
                        <AlertTriangle size={14} />
                        {lib.warnings.length} alert{lib.warnings.length > 1 && 's'}
                      </span>
                    ) : (
                      <span className="text-emerald-500 inline-flex items-center gap-0.5 font-semibold">
                        <CheckCircle size={14} />
                        OK
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {!list.length && (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-xs text-slate-400">
                    No active dependencies cataloged.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default MaintenanceDashboard;
