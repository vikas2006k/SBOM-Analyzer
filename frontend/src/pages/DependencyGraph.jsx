import React, { useState, useEffect } from 'react';
import { attackPathAPI } from '../services/api';
import ReactFlow, { Controls, Background, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';
import { Info, Network, AlertTriangle, ShieldCheck } from 'lucide-react';

const DependencyGraph = ({ activeAppId }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    const loadGraph = async () => {
      if (!activeAppId) return;
      setLoading(true);
      setSelectedNode(null);
      try {
        const res = await attackPathAPI.getAttackPaths(activeAppId);
        const data = res.data.data;
        
        // Adapt response JSON formats
        const rawNodes = data.graph_visualization?.nodes || [];
        const rawEdges = data.graph_visualization?.edges || [];
        
        // Add styling elements
        const formattedNodes = rawNodes.map(node => ({
          ...node,
          style: {
            background: '#111827',
            color: '#f8fafc',
            border: `1.5px solid ${node.data?.color || '#374151'}`,
            borderRadius: '12px',
            padding: '12px',
            fontSize: '11px',
            width: 180,
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }
        }));
        
        setNodes(formattedNodes);
        setEdges(rawEdges);
        setMetrics({
          paths: data.attack_paths_count,
          chains: data.critical_chains_count
        });
      } catch (err) {
        console.error("Failed to load visual attack paths graph:", err);
      } finally {
        setLoading(false);
      }
    };
    loadGraph();
  }, [activeAppId]);

  const onNodeClick = (event, node) => {
    setSelectedNode(node.data);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-indigo-650/30 border-t-indigo-600 animate-spin"></div>
        <p className="text-sm text-slate-400">Resolving graph topology and attack paths...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-bold text-2xl text-slate-100">Interactive Attack Path Graph</h1>
          <p className="text-xs text-slate-400 mt-1">Graphical visualization of software package chains. Red paths indicate exploit vectors propagating down to vulnerable packages.</p>
        </div>
        
        {metrics && (
          <div className="flex gap-3 text-xs">
            <span className="bg-red-500/10 border border-red-500/20 text-red-400 px-3 py-1 rounded-full font-bold">
              {metrics.paths} Attack Paths Detected
            </span>
            <span className="bg-orange-500/10 border border-orange-500/20 text-orange-400 px-3 py-1 rounded-full font-bold">
              {metrics.chains} Critical Chains
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-[500px]">
        {/* Left Side: React Flow Canvas Panel */}
        <div className="lg:col-span-3 bg-cyber-card border border-cyber-border rounded-xl relative overflow-hidden h-[500px] lg:h-auto shadow-inner">
          <ReactFlow 
            nodes={nodes}
            edges={edges}
            onNodeClick={onNodeClick}
            fitView
            minZoom={0.5}
            maxZoom={1.5}
          >
            <Background color="#1f2937" gap={16} size={1} />
            <Controls className="bg-slate-900 border border-slate-700 rounded-lg text-slate-200 fill-current" />
            <MiniMap 
              nodeColor={(node) => node.style?.border?.split(' ')[2] || '#4f46e5'}
              maskColor="rgba(0, 0, 0, 0.4)"
              className="bg-cyber-card/90 border border-cyber-border rounded-lg"
            />
          </ReactFlow>
        </div>

        {/* Right Side: Component Details Sidebar Panel */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex flex-col space-y-4 shadow-lg justify-start">
          <h3 className="font-bold text-sm text-slate-200 flex items-center gap-1.5 border-b border-cyber-border pb-3">
            <Info size={16} className="text-indigo-500" />
            Dependency Context Node Explorer
          </h3>

          {selectedNode ? (
            <div className="space-y-4 overflow-y-auto text-xs leading-normal">
              {/* Name & version */}
              <div>
                <p className="text-slate-450 uppercase font-bold tracking-wider text-[10px]">Package Name</p>
                <p className="text-base font-bold text-slate-200 mt-0.5">{selectedNode.name}</p>
                <p className="text-xs text-slate-400 mt-0.5">Version: {selectedNode.version}</p>
              </div>

              {/* Status */}
              <div>
                <p className="text-slate-450 uppercase font-bold tracking-wider text-[10px] mb-1">Security Audit Status</p>
                {selectedNode.status === 'vulnerable' ? (
                  <span className="bg-red-500/10 border border-red-500/20 text-red-500 px-2 py-0.5 rounded font-bold uppercase tracking-wider text-[10px] inline-flex items-center gap-1">
                    <AlertTriangle size={10} />
                    Vulnerable
                  </span>
                ) : selectedNode.status === 'application' ? (
                  <span className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded font-bold uppercase tracking-wider text-[10px] inline-flex items-center gap-1">
                    <Network size={10} />
                    Target App
                  </span>
                ) : (
                  <span className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 px-2 py-0.5 rounded font-bold uppercase tracking-wider text-[10px] inline-flex items-center gap-1">
                    <ShieldCheck size={10} />
                    Secure Component
                  </span>
                )}
              </div>

              {/* Ecosystem & Depth */}
              <div className="grid grid-cols-2 gap-4 border-t border-cyber-border pt-3">
                <div>
                  <p className="text-slate-450 uppercase font-bold tracking-wider text-[10px]">Ecosystem</p>
                  <p className="text-xs font-semibold text-slate-200 mt-0.5 capitalize">{selectedNode.ecosystem || 'unknown'}</p>
                </div>
                <div>
                  <p className="text-slate-450 uppercase font-bold tracking-wider text-[10px]">Graph Depth</p>
                  <p className="text-xs font-semibold text-slate-200 mt-0.5">Level {selectedNode.depth}</p>
                </div>
              </div>

              {/* Vulnerabilities Details */}
              {selectedNode.vulnerabilities?.length > 0 && (
                <div className="border-t border-cyber-border pt-3 space-y-2">
                  <p className="text-slate-450 uppercase font-bold tracking-wider text-[10px]">Vulnerability Catalog</p>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {selectedNode.vulnerabilities.map(v => (
                      <div key={v.cve_id} className="p-2 rounded bg-slate-900 border border-cyber-border space-y-1">
                        <div className="flex justify-between items-center">
                          <span className="font-bold text-red-400">{v.cve_id}</span>
                          <span className="bg-red-500/10 text-red-500 text-[10px] px-1 rounded font-bold">
                            CVSS {v.cvss_score}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-400">Class: {v.risk_category}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500 text-center">
              <Network size={32} className="mb-2 text-slate-600" />
              <p className="text-xs">Click any dependency node on the visual canvas map to inspect properties.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DependencyGraph;
