import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import DashboardLayout from './layouts/DashboardLayout';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import SBOMUpload from './pages/SBOMUpload';
import ApplicationDetails from './pages/ApplicationDetails';
import DependencyGraph from './pages/DependencyGraph';
import VulnerabilityCenter from './pages/VulnerabilityCenter';
import RiskDashboard from './pages/RiskDashboard';
import LicenseDashboard from './pages/LicenseDashboard';
import MaintenanceDashboard from './pages/MaintenanceDashboard';
import Reports from './pages/Reports';
import AICopilot from './pages/AICopilot';
import Settings from './pages/Settings';

const PrivateRoute = ({ children, activeAppId, setActiveAppId }) => {
  const { token, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-cyber-dark text-slate-100 flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-4 border-indigo-650/30 border-t-indigo-600 animate-spin"></div>
      </div>
    );
  }
  
  return token ? (
    <DashboardLayout activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
      {children}
    </DashboardLayout>
  ) : (
    <Navigate to="/login" />
  );
};

const App = () => {
  const [activeAppId, setActiveAppId] = useState(null);

  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          {/* Private Routes Group */}
          <Route path="/" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <Dashboard />
            </PrivateRoute>
          } />
          <Route path="/upload" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <SBOMUpload />
            </PrivateRoute>
          } />
          <Route path="/dependencies" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <ApplicationDetails activeAppId={activeAppId} />
            </PrivateRoute>
          } />
          <Route path="/graph" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <DependencyGraph activeAppId={activeAppId} />
            </PrivateRoute>
          } />
          <Route path="/vulnerabilities" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <VulnerabilityCenter activeAppId={activeAppId} />
            </PrivateRoute>
          } />
          <Route path="/risk" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <RiskDashboard activeAppId={activeAppId} />
            </PrivateRoute>
          } />
          <Route path="/licenses" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <LicenseDashboard activeAppId={activeAppId} />
            </PrivateRoute>
          } />
          <Route path="/maintenance" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <MaintenanceDashboard activeAppId={activeAppId} />
            </PrivateRoute>
          } />
          <Route path="/reports" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <Reports activeAppId={activeAppId} />
            </PrivateRoute>
          } />
          <Route path="/copilot" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <AICopilot activeAppId={activeAppId} />
            </PrivateRoute>
          } />
          <Route path="/settings" element={
            <PrivateRoute activeAppId={activeAppId} setActiveAppId={setActiveAppId}>
              <Settings />
            </PrivateRoute>
          } />

          {/* Wildcard redirect */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
