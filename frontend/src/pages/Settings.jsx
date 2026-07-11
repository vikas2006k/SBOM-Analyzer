import React, { useState, useEffect } from 'react';
import { licenseAPI } from '../services/api';
import { Settings, Save, Scale, Check, X, ShieldAlert } from 'lucide-react';

const SettingsPage = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  const loadRules = async () => {
    setLoading(true);
    try {
      const res = await licenseAPI.getRules();
      setRules(res.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  const handleToggle = (idx, field) => {
    setRules(prev => {
      const copy = [...prev];
      copy[idx] = {
        ...copy[idx],
        [field]: !copy[idx][field]
      };
      return copy;
    });
  };

  const handleSave = async (idx) => {
    setSaving(true);
    setMsg('');
    const rule = rules[idx];
    try {
      await licenseAPI.updateRule({
        license_category: rule.license_category,
        commercial_allowed: rule.commercial_allowed,
        proprietary_linkable: rule.proprietary_linkable
      });
      setMsg(`Saved policy rule for category '${rule.license_category}' successfully.`);
      setTimeout(() => setMsg(''), 4000);
    } catch (err) {
      console.error(err);
      alert("Failed to save license compliance rules.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-indigo-650/30 border-t-indigo-600 animate-spin"></div>
        <p className="text-sm text-slate-400">Loading policy guidelines configs...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      
      <div>
        <h1 className="font-bold text-2xl text-slate-100 flex items-center gap-2">
          <Settings className="text-indigo-500" size={24} />
          Compliance Policy Configuration
        </h1>
        <p className="text-xs text-slate-400 mt-1">Configure workspace parameters and compliance rules. Restrict specific license categories to adjust the risk rating calculations.</p>
      </div>

      {msg && (
        <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold animate-pulse-slow">
          {msg}
        </div>
      )}

      {/* Rules table mapping */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-4 shadow-lg">
        <h3 className="font-bold text-sm text-slate-200 flex items-center gap-1.5 pb-2 border-b border-cyber-border">
          <Scale size={16} className="text-indigo-500" />
          License Categories Compliance Matrix
        </h3>

        <div className="space-y-4 pt-2">
          {rules.map((rule, idx) => (
            <div key={rule.id} className="p-4 rounded-xl border border-cyber-border bg-cyber-darker/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs">
              <div className="space-y-1 max-w-md">
                <p className="font-bold text-sm text-slate-200 uppercase tracking-wide">{rule.license_category}</p>
                <p className="text-slate-400 leading-normal">{rule.description}</p>
              </div>

              {/* Toggles and Save actions */}
              <div className="flex flex-wrap gap-4 items-center shrink-0">
                <div className="flex items-center gap-1.5 select-none">
                  <span className="text-slate-400 font-semibold uppercase text-[10px]">Commercial:</span>
                  <button 
                    onClick={() => handleToggle(idx, 'commercial_allowed')}
                    className={`px-2.5 py-1 rounded font-bold uppercase text-[9px] border transition-all ${
                      rule.commercial_allowed 
                        ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' 
                        : 'bg-red-500/10 border-red-500/20 text-red-500'
                    }`}
                  >
                    {rule.commercial_allowed ? 'Allowed' : 'Blocked'}
                  </button>
                </div>

                <div className="flex items-center gap-1.5 select-none">
                  <span className="text-slate-400 font-semibold uppercase text-[10px]">Linkable:</span>
                  <button 
                    onClick={() => handleToggle(idx, 'proprietary_linkable')}
                    className={`px-2.5 py-1 rounded font-bold uppercase text-[9px] border transition-all ${
                      rule.proprietary_linkable 
                        ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' 
                        : 'bg-red-500/10 border-red-500/20 text-red-500'
                    }`}
                  >
                    {rule.proprietary_linkable ? 'Linkable' : 'Forbidden'}
                  </button>
                </div>

                <button 
                  onClick={() => handleSave(idx)}
                  disabled={saving}
                  className="p-2 bg-indigo-650 hover:bg-indigo-755 disabled:opacity-50 text-white rounded-lg transition-colors shadow"
                  title="Save Rules Settings"
                >
                  <Save size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default SettingsPage;
