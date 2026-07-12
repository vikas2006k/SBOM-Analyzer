import React, { useState, useEffect } from 'react';
import { appAPI } from '../services/api';
import { Search, Filter, ShieldAlert, ArrowUpDown, CornerDownRight } from 'lucide-react';

const ApplicationDetails = ({ activeAppId }) => {
  const [dependencies, setDependencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Filter states
  const [ecosystemFilter, setEcosystemFilter] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All'); // 'All', 'Direct', 'Transitive'
  const [sortBy, setSortBy] = useState('name'); // 'name', 'depth'
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    const loadDependencies = async () => {
      if (!activeAppId) return;
      setLoading(true);
      // Reset all filters for the new application
      setSearch('');
      setEcosystemFilter('All');
      setTypeFilter('All');
      setSortBy('name');
      setCurrentPage(1);
      try {
        const res = await appAPI.getApplicationDependencies(activeAppId);
        setDependencies(res.data.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadDependencies();
  }, [activeAppId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-indigo-650/30 border-t-indigo-600 animate-spin"></div>
        <p className="text-sm text-slate-400">Loading dependencies catalog...</p>
      </div>
    );
  }

  // Calculate stats
  const totalCount = dependencies.length;
  const directCount = dependencies.filter(d => !d.is_transitive).length;
  const transitiveCount = dependencies.filter(d => d.is_transitive).length;
  const ecosystems = Array.from(new Set(dependencies.map(d => d.ecosystem)));

  // Filter & Sort operations
  const filteredDeps = dependencies
    .filter(d => {
      const matchSearch = d.name.toLowerCase().includes(search.toLowerCase()) || 
                          d.version.toLowerCase().includes(search.toLowerCase());
      const matchEcosys = ecosystemFilter === 'All' || d.ecosystem === ecosystemFilter;
      const matchType = typeFilter === 'All' || 
                        (typeFilter === 'Direct' && !d.is_transitive) || 
                        (typeFilter === 'Transitive' && d.is_transitive);
      return matchSearch && matchEcosys && matchType;
    })
    .sort((a, b) => {
      if (sortBy === 'name') {
        return a.name.localeCompare(b.name);
      } else if (sortBy === 'depth') {
        return a.depth - b.depth;
      }
      return 0;
    });

  // Paginated chunk
  const totalPages = Math.ceil(filteredDeps.length / itemsPerPage);
  const paginatedDeps = filteredDeps.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-bold text-2xl text-slate-100">Dependencies Manifest Inventory</h1>
        <p className="text-xs text-slate-400 mt-1">Explorable database listing of all software libraries parsed from application SBOM.</p>
      </div>

      {/* Grid: Statistics cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-4">
          <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">Total Dependencies</span>
          <p className="text-2xl font-extrabold mt-1 text-slate-200">{totalCount}</p>
        </div>
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-4">
          <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">Direct Imports</span>
          <p className="text-2xl font-extrabold mt-1 text-indigo-400">{directCount}</p>
        </div>
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-4">
          <span className="text-xs text-slate-450 uppercase font-bold tracking-wider">Transitive Downstream</span>
          <p className="text-2xl font-extrabold mt-1 text-slate-400">{transitiveCount}</p>
        </div>
      </div>

      {/* Search & Filters block */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
        
        {/* Search input */}
        <div className="relative w-full md:w-80">
          <input 
            type="text" 
            placeholder="Search by package name..." 
            value={search}
            onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
            className="w-full py-1.5 pl-10 pr-4 bg-cyber-darker border border-cyber-border text-slate-250 rounded-lg text-sm focus:outline-none focus:border-indigo-500"
          />
          <Search size={16} className="absolute left-3.5 top-2.5 text-slate-500" />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 items-center w-full md:w-auto justify-end">
          {/* Ecosystem Filter */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 font-bold uppercase">Ecosystem:</span>
            <select 
              value={ecosystemFilter}
              onChange={(e) => { setEcosystemFilter(e.target.value); setCurrentPage(1); }}
              className="bg-cyber-darker border border-cyber-border rounded px-2 py-1 focus:outline-none"
            >
              <option value="All">All Ecosystems</option>
              {ecosystems.map(eco => (
                <option key={eco} value={eco}>{eco}</option>
              ))}
            </select>
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 font-bold uppercase">Depth:</span>
            <select 
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value); setCurrentPage(1); }}
              className="bg-cyber-darker border border-cyber-border rounded px-2 py-1 focus:outline-none"
            >
              <option value="All">All Depths</option>
              <option value="Direct">Direct Only</option>
              <option value="Transitive">Transitive Only</option>
            </select>
          </div>

          {/* Sort By Filter */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 font-bold uppercase">Sort:</span>
            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-cyber-darker border border-cyber-border rounded px-2 py-1 focus:outline-none"
            >
              <option value="name">Package Name</option>
              <option value="depth">Dependency Depth</option>
            </select>
          </div>
        </div>

      </div>

      {/* Table grid */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-cyber-border text-slate-400 text-xs uppercase tracking-wider">
                <th className="py-3 px-4">Dependency Package</th>
                <th className="py-3 px-4">Installed Version</th>
                <th className="py-3 px-4">Ecosystem</th>
                <th className="py-3 px-4">Declared License</th>
                <th className="py-3 px-4">Graph Depth</th>
                <th className="py-3 px-4">Import Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border">
              {paginatedDeps.map(dep => (
                <tr key={dep.id} className="hover:bg-slate-800/20 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-slate-200">
                    <span className="inline-flex items-center gap-1">
                      {dep.is_transitive && <CornerDownRight size={12} className="text-slate-500 mr-1" />}
                      {dep.name}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-350">{dep.version}</td>
                  <td className="py-3.5 px-4">
                    <span className="bg-slate-800 px-2 py-0.5 rounded text-xs text-slate-400 capitalize">{dep.ecosystem}</span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs">{dep.license || 'Unknown'}</td>
                  <td className="py-3.5 px-4 font-semibold">Depth {dep.depth}</td>
                  <td className="py-3.5 px-4">
                    {dep.is_transitive ? (
                      <span className="text-xs text-slate-450 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                        Transitive
                      </span>
                    ) : (
                      <span className="text-xs text-indigo-400 bg-indigo-950/20 border border-indigo-900/40 px-2 py-0.5 rounded font-bold">
                        Direct
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {!filteredDeps.length && (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-xs text-slate-400">
                    No dependencies match selected search filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Toolbar */}
        {totalPages > 1 && (
          <div className="flex justify-between items-center mt-5 pt-4 border-t border-cyber-border text-xs">
            <span className="text-slate-400">
              Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredDeps.length)} of {filteredDeps.length} libraries
            </span>
            <div className="flex gap-2">
              <button 
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200"
              >
                Previous
              </button>
              <button 
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApplicationDetails;
