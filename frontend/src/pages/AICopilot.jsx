import React, { useState, useEffect, useRef } from 'react';
import { copilotAPI } from '../services/api';
import { Send, Bot, User, ShieldAlert, Sparkles } from 'lucide-react';

// A lightweight helper to parse basic markdown format characters to styled HTML
const formatMarkdown = (text) => {
  if (!text) return '';
  let html = text;
  
  // Headers (e.g. ### Title)
  html = html.replace(/^### (.*?)$/gm, '<h4 class="font-bold text-sm text-indigo-400 mt-3 mb-1.5">$1</h4>');
  html = html.replace(/^## (.*?)$/gm, '<h3 class="font-bold text-base text-indigo-400 mt-4 mb-2">$1</h3>');
  html = html.replace(/^# (.*?)$/gm, '<h2 class="font-bold text-lg text-slate-100 mt-4 mb-2 border-b border-slate-800 pb-1">$1</h2>');
  
  // Bold (e.g. **text**)
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-slate-150">$1</strong>');
  
  // Bullet lists (e.g. - item or * item)
  html = html.replace(/^\s*[-*]\s+(.*?)$/gm, '<li class="ml-4 list-disc list-inside text-slate-300 leading-relaxed">$1</li>');
  
  // Code snippets (e.g. `code`)
  html = html.replace(/`(.*?)`/g, '<code class="bg-slate-900 px-1.5 py-0.5 rounded text-indigo-400 font-mono text-xs">$1</code>');
  
  // Code blocks (e.g. ```code```)
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="bg-slate-900 border border-slate-800 rounded-xl p-3 my-2 font-mono text-[11px] text-slate-200 overflow-x-auto select-all leading-normal">$1</pre>');
  
  // Linebreaks
  html = html.replace(/\n/g, '<br />');
  
  return html;
};

const AICopilot = ({ activeAppId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Suggested prompts chips list
  const suggestedPrompts = [
    "What is my highest risk?",
    "What should be fixed first?",
    "Recommend remediation",
    "Generate executive summary",
    "Explain CVE-2023-51074"
  ];

  const loadHistory = async () => {
    if (!activeAppId) return;
    try {
      const res = await copilotAPI.getHistory(activeAppId);
      const list = res.data.data || [];
      
      if (list.length === 0) {
        setMessages([
          { 
            sender: 'copilot', 
            text: "Hello! I am your AI Security Copilot. I have analyzed the codebase supply chain. Select one of the questions below or ask custom questions about code risks, licensing compliance, or vulnerabilities." 
          }
        ]);
      } else {
        setMessages(list);
      }
    } catch (err) {
      console.error("History load failed:", err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [activeAppId]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (messageText) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || !activeAppId) return;
    
    // Add user message locally
    const updatedMessages = [...messages, { sender: 'user', text: textToSend }];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);
    
    try {
      const res = await copilotAPI.chat(activeAppId, textToSend);
      const data = res.data.data;
      
      setMessages(prev => [
        ...prev, 
        { 
          sender: 'copilot', 
          text: data.response,
          referenced_items: data.referenced_items 
        }
      ]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev, 
        { 
          sender: 'copilot', 
          text: "Communication timeout: The AI multi-agent orchestration service returned an execution error. Please try again." 
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 h-[calc(100vh-140px)] flex flex-col">
      <div>
        <h1 className="font-bold text-2xl text-slate-100 flex items-center gap-2">
          <Sparkles className="text-indigo-500" size={24} />
          AI Security Copilot (LangGraph Agents)
        </h1>
        <p className="text-xs text-slate-400 mt-1">Multi-agent security intelligence workspace. Resolve supply chain vulnerability questions dynamically.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-[450px]">
        {/* Left Side: Suggestions Panel */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex flex-col justify-between hidden lg:flex shadow-lg h-[450px] lg:h-auto">
          <div className="space-y-4">
            <h3 className="font-bold text-sm text-slate-205 border-b border-cyber-border pb-3 flex items-center gap-1.5">
              <Bot size={16} className="text-indigo-500" />
              Suggested Auditing Queries
            </h3>
            
            <div className="flex flex-col gap-2.5">
              {suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => handleSend(prompt)}
                  disabled={loading}
                  className="w-full text-left px-3 py-2 bg-cyber-darker border border-cyber-border rounded-lg text-xs font-semibold text-slate-300 hover:border-indigo-500 hover:text-slate-100 transition-all"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          <div className="p-3.5 bg-slate-900 border border-cyber-border rounded-xl text-[11px] text-slate-450 leading-relaxed">
            <p className="font-bold text-indigo-400 mb-1">Multi-Agent State:</p>
            The Orchestrator Agent automatically coordinates specialized SBOM, Vulnerability, and Compliance Advisory Sub-Agents to resolve your queries.
          </div>
        </div>

        {/* Right Side: Chat Container Panel */}
        <div className="lg:col-span-3 bg-cyber-card border border-cyber-border rounded-xl flex flex-col h-[450px] lg:h-auto overflow-hidden shadow-2xl">
          
          {/* Messages list */}
          <div className="flex-1 overflow-y-auto p-6 space-y-5">
            {messages.map((msg, index) => {
              const isCopilot = msg.sender === 'copilot';
              return (
                <div key={index} className={`flex gap-3.5 max-w-4xl ${isCopilot ? 'justify-start' : 'justify-end'}`}>
                  {isCopilot && (
                    <div className="w-8 h-8 rounded-full bg-indigo-650 flex items-center justify-center text-white text-sm shrink-0">
                      <Bot size={16} />
                    </div>
                  )}
                  
                  <div className={`p-4 rounded-xl text-xs leading-normal shadow max-w-[85%] ${
                    isCopilot 
                      ? 'bg-slate-900 border border-cyber-border text-slate-300' 
                      : 'bg-indigo-650 text-white font-medium'
                  }`}>
                    {isCopilot ? (
                      <div 
                        dangerouslySetInnerHTML={{ __html: formatMarkdown(msg.text) }}
                        className="space-y-1.5"
                      />
                    ) : (
                      <p>{msg.text}</p>
                    )}
                  </div>

                  {!isCopilot && (
                    <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-white text-sm shrink-0 uppercase font-semibold">
                      <User size={16} />
                    </div>
                  )}
                </div>
              );
            })}
            
            {loading && (
              <div className="flex gap-3 justify-start items-center">
                <div className="w-8 h-8 rounded-full bg-indigo-650 flex items-center justify-center text-white text-sm shrink-0">
                  <Bot size={16} />
                </div>
                <div className="bg-slate-900 border border-cyber-border px-4 py-3 rounded-xl flex gap-1.5 items-center">
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce"></span>
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce delay-100"></span>
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce delay-200"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Form input */}
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="p-4 border-t border-cyber-border flex gap-3 items-center bg-cyber-darker/60"
          >
            <input 
              type="text" 
              placeholder="Ask AI Copilot anything about package security..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              className="flex-1 py-2 px-4 text-sm bg-cyber-card border border-cyber-border rounded-lg focus:outline-none focus:border-indigo-500 text-slate-200"
            />
            <button 
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2.5 bg-indigo-600 hover:bg-indigo-755 disabled:opacity-50 text-white rounded-lg transition-colors shadow"
            >
              <Send size={16} />
            </button>
          </form>

        </div>
      </div>
    </div>
  );
};

export default AICopilot;
