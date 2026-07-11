import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert, Eye, EyeOff, Lock, User, AlertCircle } from 'lucide-react';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username.trim() || !password.trim()) {
      setError('Please fill in all security fields.');
      return;
    }
    
    setLoading(true);
    const res = await login(username, password);
    setLoading(false);
    
    if (res.success) {
      navigate('/');
    } else {
      setError(res.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-cyber-dark text-slate-100 font-sans p-4 relative overflow-hidden">
      
      {/* Background radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-indigo-650/10 blur-[120px] pointer-events-none"></div>
      
      <div className="w-full max-w-md bg-cyber-card/80 backdrop-blur-md border border-cyber-border rounded-2xl shadow-2xl p-8 relative z-10">
        
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="bg-indigo-600 p-3 rounded-2xl text-white shadow-lg mb-3 shadow-indigo-600/30">
            <ShieldAlert size={28} />
          </div>
          <h1 className="font-bold text-2xl tracking-wider text-slate-100">SentinelSBOM</h1>
          <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest">Supply Chain Risk Intelligence</p>
        </div>

        {/* Error alerting banner */}
        {error && (
          <div className="mb-6 bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3 rounded-lg flex items-center gap-2 text-sm leading-normal animate-shake">
            <AlertCircle size={18} className="shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Username */}
          <div>
            <label className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-1.5">Username</label>
            <div className="relative">
              <input 
                type="text"
                placeholder="Enter security username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full py-2.5 pl-10 pr-4 text-sm bg-cyber-darker border border-cyber-border rounded-lg focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-200"
              />
              <User size={16} className="absolute left-3.5 top-3 text-slate-500" />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-1.5">Security Password</label>
            <div className="relative">
              <input 
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full py-2.5 pl-10 pr-10 text-sm bg-cyber-darker border border-cyber-border rounded-lg focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-200"
              />
              <Lock size={16} className="absolute left-3.5 top-3 text-slate-500" />
              <button 
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3.5 text-slate-500 hover:text-slate-350"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-2.5 mt-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-650/50 text-white font-semibold rounded-lg text-sm transition-colors shadow-lg shadow-indigo-600/20 flex items-center justify-center gap-2"
          >
            {loading ? (
              <span className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
            ) : (
              <span>Sign In to Terminal</span>
            )}
          </button>
        </form>

        <div className="mt-8 pt-4 border-t border-cyber-border text-center text-xs text-slate-500">
          <p>SentinelSBOM Security Scorer Terminal. Seed Credentials: <code className="text-indigo-400 bg-slate-900 px-1 py-0.5 rounded">admin</code> / <code className="text-indigo-400 bg-slate-900 px-1 py-0.5 rounded">admin123</code></p>
        </div>

      </div>
    </div>
  );
};

export default Login;
