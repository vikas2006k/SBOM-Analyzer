import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { dashboardAPI, notificationAPI } from '../services/api';
import { 
  LayoutDashboard, UploadCloud, Network, ShieldAlert, Scale, Wrench, FileSpreadsheet, 
  Bot, Settings, LogOut, Bell, Search, Sun, Moon, Database, ChevronDown, Check, X, AlertTriangle
} from 'lucide-react';

const DashboardLayout = ({ children, activeAppId, setActiveAppId }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [apps, setApps] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    // Force dark mode class on html
    const html = document.documentElement;
    if (darkMode) {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  }, [darkMode]);

  // Load applications and notifications
  useEffect(() => {
    const loadHeaderData = async () => {
      try {
        const appsRes = await dashboardAPI.getSummary();
        const appsList = appsRes.data.data.applications_status || [];
        setApps(appsList);
        
        if (appsList.length > 0 && !activeAppId) {
          setActiveAppId(appsList[0].id);
        }
        
        const notifRes = await notificationAPI.getNotifications(true);
        setNotifications(notifRes.data.data || []);
      } catch (err) {
        console.error("Failed to load header dashboard context:", err);
      }
    };
    loadHeaderData();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      const res = await dashboardAPI.search(searchQuery);
      setSearchResults(res.data.data);
      setShowSearchModal(true);
    } catch (err) {
      console.error("Search failed:", err);
    }
  };

  const handleNotificationClick = async (notifId) => {
    try {
      await notificationAPI.markRead(notifId);
      setNotifications(prev => prev.filter(n => n.id !== notifId));
    } catch (err) {
      console.error(err);
    }
  };

  const activeApp = apps.find(a => a.id === activeAppId);

  const menuItems = [
    { name: 'Dashboard Overview', path: '/', icon: LayoutDashboard },
    { name: 'SBOM Upload Center', path: '/upload', icon: UploadCloud },
    { name: 'Dependencies', path: `/dependencies`, icon: Database },
    { name: 'Interactive Graph', path: `/graph`, icon: Network },
    { name: 'Vulnerability Center', path: `/vulnerabilities`, icon: ShieldAlert },
    { name: 'Risk Analytics', path: `/risk`, icon: AlertTriangle },
    { name: 'License Dashboard', path: `/licenses`, icon: Scale },
    { name: 'Maintenance Health', path: `/maintenance`, icon: Wrench },
    { name: 'Reports Center', path: `/reports`, icon: FileSpreadsheet },
    { name: 'AI Copilot Advisor', path: `/copilot`, icon: Bot },
    { name: 'Policy Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className={`min-h-screen flex ${darkMode ? 'bg-cyber-dark text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      
      {/* Sidebar Navigation */}
      <aside className={`w-64 border-r ${darkMode ? 'bg-cyber-darker border-cyber-border' : 'bg-white border-slate-200'} hidden md:flex flex-col`}>
        <div className="p-6 border-b border-cyber-border flex items-center gap-2">
          <div className="bg-indigo-600 p-2 rounded-lg text-white">
            <ShieldAlert size={20} />
          </div>
          <span className="font-bold text-lg tracking-wider text-indigo-500">SentinelSBOM</span>
        </div>
        
        {/* Active Application Picker */}
        <div className="p-4 border-b border-cyber-border">
          <label className="text-xs text-slate-400 block mb-1">Audit Project Target</label>
          <div className="relative">
            <select 
              value={activeAppId || ''} 
              onChange={(e) => setActiveAppId(Number(e.target.value))}
              className={`w-full appearance-none px-3 py-2 pr-8 rounded-lg text-sm font-medium border focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer ${
                darkMode ? 'bg-cyber-card border-cyber-border text-slate-200' : 'bg-slate-100 border-slate-300 text-slate-800'
              }`}
            >
              {apps.map(app => (
                <option key={app.id} value={app.id}>
                  {app.name} v{app.version}
                </option>
              ))}
            </select>
            <ChevronDown size={14} className="absolute right-3 top-3 text-slate-400 pointer-events-none" />
          </div>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
          {menuItems.map(item => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link 
                key={item.name} 
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive 
                    ? 'bg-indigo-600 text-white' 
                    : darkMode 
                      ? 'text-slate-400 hover:bg-slate-800 hover:text-slate-200' 
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <Icon size={18} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* User profile footer */}
        <div className="p-4 border-t border-cyber-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-indigo-500 text-white flex items-center justify-center font-bold text-sm uppercase">
              {user?.username?.[0] || 'A'}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold truncate leading-none mb-1">{user?.username || 'Analyst'}</p>
              <span className="text-xs text-slate-400 capitalize">{user?.role || 'viewer'}</span>
            </div>
          </div>
          <button 
            onClick={() => { logout(); navigate('/login'); }}
            className={`p-1.5 rounded-lg hover:bg-red-500/10 hover:text-red-500 transition-colors ${
              darkMode ? 'text-slate-400' : 'text-slate-600'
            }`}
            title="Logout"
          >
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Header toolbar */}
        <header className={`h-16 border-b px-6 flex items-center justify-between ${
          darkMode ? 'bg-cyber-darker border-cyber-border' : 'bg-white border-slate-200'
        }`}>
          
          {/* Header left: Search */}
          <form onSubmit={handleSearch} className="relative w-80">
            <input 
              type="text" 
              placeholder="Search CVEs, libraries, apps..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full py-1.5 pl-10 pr-4 text-sm rounded-lg border focus:outline-none focus:ring-1 focus:ring-indigo-500 ${
                darkMode ? 'bg-cyber-card border-cyber-border text-slate-200' : 'bg-slate-100 border-slate-300 text-slate-800'
              }`}
            />
            <Search size={16} className="absolute left-3 top-2.5 text-slate-400" />
            <button type="submit" className="hidden" />
          </form>

          {/* Header right: Actions */}
          <div className="flex items-center gap-4">
            
            {/* Dark mode Toggle */}
            <button 
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2 rounded-lg border transition-colors ${
                darkMode ? 'border-cyber-border bg-cyber-card text-amber-400' : 'border-slate-300 bg-slate-100 text-indigo-600'
              }`}
            >
              {darkMode ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            {/* Notification alert bells */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className={`p-2 rounded-lg border relative transition-colors ${
                  darkMode ? 'border-cyber-border bg-cyber-card text-slate-300' : 'border-slate-300 bg-slate-100 text-slate-600'
                }`}
              >
                <Bell size={16} />
                {notifications.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white w-4 h-4 rounded-full flex items-center justify-center font-bold text-[9px]">
                    {notifications.length}
                  </span>
                )}
              </button>

              {/* Notification dropdown list */}
              {showNotifications && (
                <div className={`absolute right-0 mt-2 w-80 rounded-xl shadow-2xl border p-4 z-50 ${
                  darkMode ? 'bg-cyber-card border-cyber-border' : 'bg-white border-slate-200'
                }`}>
                  <div className="flex items-center justify-between mb-3 pb-2 border-b border-cyber-border">
                    <span className="font-bold text-sm">Notifications Alerts</span>
                    <button 
                      onClick={() => setShowNotifications(false)}
                      className="text-slate-400 hover:text-slate-200"
                    >
                      <X size={14} />
                    </button>
                  </div>
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {notifications.length > 0 ? (
                      notifications.map(notif => (
                        <div key={notif.id} className="text-xs p-2 rounded hover:bg-slate-800 transition-colors cursor-pointer" onClick={() => handleNotificationClick(notif.id)}>
                          <p className="font-bold text-indigo-400 leading-snug">{notif.title}</p>
                          <p className="text-slate-400 mt-1 leading-normal">{notif.message}</p>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-400 text-center py-4">No active risk alerts.</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Selected app visual indicator pill */}
            {activeApp && (
              <div className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 ${
                activeApp.risk_score >= 75.0 
                  ? 'bg-red-500/10 text-red-500' 
                  : activeApp.risk_score >= 50.0 
                    ? 'bg-orange-500/10 text-orange-500' 
                    : 'bg-emerald-500/10 text-emerald-500'
              }`}>
                <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
                <span>Risk: {activeApp.risk_score}/100</span>
              </div>
            )}
          </div>
        </header>

        {/* Content Wrapper */}
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>

      {/* Global Search Modal Overlay */}
      {showSearchModal && searchResults && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className={`w-full max-w-3xl rounded-xl shadow-2xl border flex flex-col max-h-[85vh] ${
            darkMode ? 'bg-cyber-card border-cyber-border' : 'bg-white border-slate-200'
          }`}>
            {/* Header */}
            <div className="p-4 border-b border-cyber-border flex items-center justify-between">
              <span className="font-bold text-base flex items-center gap-2">
                <Search size={18} className="text-indigo-500" />
                Global Search Results
              </span>
              <button 
                onClick={() => { setShowSearchModal(false); setSearchResults(null); }}
                className="text-slate-400 hover:text-slate-200"
              >
                <X size={20} />
              </button>
            </div>
            {/* Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              
              {/* Applications section */}
              {searchResults.applications?.length > 0 && (
                <div>
                  <h3 className="text-xs text-indigo-400 font-bold tracking-wider mb-2 uppercase">Applications ({searchResults.applications.length})</h3>
                  <div className="space-y-2">
                    {searchResults.applications.map(app => (
                      <div key={app.id} className="p-3 rounded-lg border border-cyber-border bg-cyber-dark/40 hover:border-indigo-500 cursor-pointer" onClick={() => { setActiveAppId(app.id); setShowSearchModal(false); }}>
                        <p className="font-bold text-sm">{app.name} <span className="text-xs text-slate-400">v{app.version}</span></p>
                        <p className="text-xs text-slate-400 mt-1">{app.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Libraries section */}
              {searchResults.libraries?.length > 0 && (
                <div>
                  <h3 className="text-xs text-indigo-400 font-bold tracking-wider mb-2 uppercase">Libraries ({searchResults.libraries.length})</h3>
                  <div className="space-y-2">
                    {searchResults.libraries.map(lib => (
                      <div key={lib.id} className="p-3 rounded-lg border border-cyber-border bg-cyber-dark/40">
                        <div className="flex items-center justify-between">
                          <p className="font-bold text-sm text-slate-200">{lib.name} <span className="text-xs text-slate-500">@{lib.version}</span></p>
                          <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-400 capitalize">{lib.ecosystem}</span>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">License: {lib.license}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Vulnerabilities section */}
              {searchResults.vulnerabilities?.length > 0 && (
                <div>
                  <h3 className="text-xs text-indigo-400 font-bold tracking-wider mb-2 uppercase">Vulnerabilities ({searchResults.vulnerabilities.length})</h3>
                  <div className="space-y-2">
                    {searchResults.vulnerabilities.map(v => (
                      <div key={v.id} className="p-3 rounded-lg border border-cyber-border bg-cyber-dark/40">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-sm text-red-400">{v.cve_id}</span>
                          <span className="text-xs font-bold text-slate-300">CVSS {v.cvss_score}</span>
                        </div>
                        <p className="text-xs text-slate-350 mt-1 leading-normal">{v.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty state */}
              {(!searchResults.applications?.length && !searchResults.libraries?.length && !searchResults.vulnerabilities?.length) && (
                <div className="text-center py-12">
                  <p className="text-sm text-slate-400">No matching security catalog entries found.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardLayout;
