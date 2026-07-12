import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { 
  AppWindow, ShieldAlert, Scale, Wrench, ChevronRight, Activity, TrendingUp, AlertTriangle, Play 
} from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const Dashboard = ({ activeAppId }) => {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  console.log("Dashboard rendered with activeAppId:", activeAppId);

  useEffect(() => {
    const loadDashboardMetrics = async () => {
      console.log("loadDashboardMetrics triggered with activeAppId:", activeAppId);
      setLoading(true);
      try {
        const res = await dashboardAPI.getSummary(activeAppId);
        setMetrics(res.data.data);
      } catch (err) {
        console.error("Dashboard metrics load failed:", err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboardMetrics();
  }, [activeAppId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-indigo-650/30 border-t-indigo-600 animate-spin"></div>
        <p className="text-sm text-slate-400">Compiling executive intelligence dashboards...</p>
      </div>
    );
  }

  // Compile Chart Data
  const severityData = metrics?.severity_distribution || { Critical: 0, High: 0, Medium: 0, Low: 0, Informational: 0 };
  const pieChartData = {
    labels: ['Critical', 'High', 'Medium', 'Low', 'Informational'],
    datasets: [{
      data: [severityData.Critical, severityData.High, severityData.Medium, severityData.Low, severityData.Informational],
      backgroundColor: ['#ef4444', '#f97316', '#eab308', '#3b82f6', '#94a3b8'],
      borderColor: '#111827',
      borderWidth: 1,
    }]
  };

  const licenseData = metrics?.license_distribution || {};
  const barChartData = {
    labels: Object.keys(licenseData).slice(0, 5),
    datasets: [{
      label: 'License Distribution',
      data: Object.values(licenseData).slice(0, 5),
      backgroundColor: '#4f46e5',
      borderColor: '#6366f1',
      borderWidth: 1,
      borderRadius: 6
    }]
  };

  return (
    <div className="space-y-6">
      
      {/* Header title */}
      <div>
        <h1 className="font-bold text-2xl text-slate-100">Cybersecurity Risk Executive Dashboard</h1>
        <p className="text-xs text-slate-400 mt-1">Aggregated software supply chain threat intelligence and SBOM vulnerabilities analysis.</p>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        
        {/* Total Apps */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow-lg">
          <div>
            <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">Monitored Applications</span>
            <p className="text-3xl font-extrabold mt-1">{metrics?.total_applications}</p>
          </div>
          <div className="bg-indigo-500/10 p-3 rounded-lg text-indigo-500">
            <AppWindow size={24} />
          </div>
        </div>

        {/* Tracked Vulns */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow-lg">
          <div>
            <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">Active Vulnerabilities</span>
            <p className="text-3xl font-extrabold mt-1 text-red-500">{metrics?.active_vulnerabilities}</p>
          </div>
          <div className="bg-red-500/10 p-3 rounded-lg text-red-500 animate-pulse">
            <ShieldAlert size={24} />
          </div>
        </div>

        {/* License Conflicts */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow-lg">
          <div>
            <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">CVE Catalog Library</span>
            <p className="text-3xl font-extrabold mt-1 text-indigo-400">{metrics?.vulnerabilities_catalog}</p>
          </div>
          <div className="bg-indigo-500/10 p-3 rounded-lg text-indigo-400">
            <Scale size={24} />
          </div>
        </div>

        {/* Global Average Risk */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex items-center justify-between shadow-lg">
          <div>
            <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">Workspace Average Risk</span>
            <p className="text-3xl font-extrabold mt-1 text-amber-500">{metrics?.average_risk_score}</p>
          </div>
          <div className="bg-amber-500/10 p-3 rounded-lg text-amber-500">
            <TrendingUp size={24} />
          </div>
        </div>

      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Severity Pie Chart */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5">
          <h3 className="font-bold text-sm text-slate-200 mb-4 flex items-center gap-1.5">
            <Activity size={16} className="text-indigo-500" />
            Vulnerabilities Severity Distribution
          </h3>
          <div className="h-64 flex justify-center items-center">
            {metrics?.active_vulnerabilities > 0 ? (
              <Pie data={pieChartData} options={{ responsive: true, maintainAspectRatio: false }} />
            ) : (
              <p className="text-xs text-slate-400">No active code package vulnerabilities found.</p>
            )}
          </div>
        </div>

        {/* License Bar Chart */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5">
          <h3 className="font-bold text-sm text-slate-200 mb-4 flex items-center gap-1.5">
            <Scale size={16} className="text-indigo-500" />
            Top Ingested SPDX Licenses
          </h3>
          <div className="h-64 flex justify-center items-center">
            {Object.keys(licenseData).length > 0 ? (
              <Bar data={barChartData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
            ) : (
              <p className="text-xs text-slate-400">No dependency components loaded.</p>
            )}
          </div>
        </div>
      </div>

      {/* Target Application Security Catalog */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-5">
        <h3 className="font-bold text-sm text-slate-200 mb-4 flex items-center gap-1.5">
          <AppWindow size={16} className="text-indigo-500" />
          Application Supply Chain Risk Profiles
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-cyber-border text-slate-400 text-xs uppercase tracking-wider">
                <th className="py-3 px-4">Application Profile</th>
                <th className="py-3 px-4">Criticality</th>
                <th className="py-3 px-4">Vulnerability Count</th>
                <th className="py-3 px-4">Composite Risk Score</th>
                <th className="py-3 px-4">Threat Level</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border">
              {metrics?.applications_status?.map(app => (
                <tr key={app.id} className="hover:bg-slate-800/20 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-slate-200">
                    {app.name} <span className="text-xs text-slate-500">v{app.version}</span>
                  </td>
                  <td className="py-3.5 px-4 text-xs font-semibold">{app.business_criticality}</td>
                  <td className="py-3.5 px-4">
                    {app.vulnerabilities_count > 0 ? (
                      <span className="bg-red-500/10 text-red-400 px-2 py-0.5 rounded text-xs font-semibold">
                        {app.vulnerabilities_count} CVEs
                      </span>
                    ) : (
                      <span className="text-xs text-slate-550">0 CVEs</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 font-bold text-slate-200">{app.risk_score}/100</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                      app.risk_severity === 'Critical' 
                        ? 'bg-red-500/10 text-red-500' 
                        : app.risk_severity === 'High' 
                          ? 'bg-orange-500/10 text-orange-500' 
                          : app.risk_severity === 'Medium' 
                            ? 'bg-amber-500/10 text-amber-500' 
                            : 'bg-emerald-500/10 text-emerald-500'
                    }`}>
                      {app.risk_severity}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button 
                      onClick={() => navigate(`/dependencies`)}
                      className="text-indigo-400 hover:text-indigo-200 text-xs font-bold inline-flex items-center gap-0.5"
                    >
                      Audit
                      <ChevronRight size={14} />
                    </button>
                  </td>
                </tr>
              ))}
              {!metrics?.applications_status?.length && (
                <tr>
                  <td colSpan="6" className="py-6 text-center text-xs text-slate-400">
                    No active software projects cataloged. Drag and drop SBOM manifests to generate reports.
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

export default Dashboard;
