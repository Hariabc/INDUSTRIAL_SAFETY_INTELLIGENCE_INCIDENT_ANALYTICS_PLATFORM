import React from 'react';
import { Search, Filter, Calendar, Bell, RotateCcw, ShieldCheck } from 'lucide-react';
import { useFilters } from '../../context/FilterContext';

export const Navbar: React.FC = () => {
  const {
    filters,
    setPlantId,
    setSeverity,
    setDateRange,
    setSearchQuery,
    resetFilters,
  } = useFilters();

  return (
    <header className="h-16 bg-industrial-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-20 flex items-center justify-between px-6 pl-72">
      {/* Search Input */}
      <div className="flex items-center gap-3 flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search machines, alarm IDs, incidents, interlocks..."
            value={filters.searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950/60 border border-slate-800 rounded-lg pl-9 pr-4 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/40 font-mono transition-all"
          />
        </div>
      </div>

      {/* Global Interactive Filters */}
      <div className="flex items-center gap-3">
        {/* Plant Selector */}
        <div className="flex items-center gap-1.5 bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-1 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={filters.plantId}
            onChange={(e) => setPlantId(e.target.value)}
            className="bg-transparent text-slate-200 text-xs focus:outline-none cursor-pointer font-medium"
          >
            <option value="" className="bg-industrial-900 text-slate-200">All Plants (4)</option>
            <option value="PLN-001" className="bg-industrial-900 text-slate-200">Apex Propulsion (Detroit)</option>
            <option value="PLN-002" className="bg-industrial-900 text-slate-200">Bavaria Precision (Munich)</option>
            <option value="PLN-003" className="bg-industrial-900 text-slate-200">Shenzhen Gigafactory (China)</option>
            <option value="PLN-004" className="bg-industrial-900 text-slate-200">Solway Synthesis (UK)</option>
          </select>
        </div>

        {/* Severity Selector */}
        <select
          value={filters.severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none cursor-pointer font-medium"
        >
          <option value="" className="bg-industrial-900 text-slate-200">All Severities</option>
          <option value="CRITICAL" className="bg-industrial-900 text-red-400 font-mono font-semibold">CRITICAL</option>
          <option value="HIGH" className="bg-industrial-900 text-orange-400 font-mono font-semibold">HIGH</option>
          <option value="MEDIUM" className="bg-industrial-900 text-amber-400 font-mono">MEDIUM</option>
          <option value="LOW" className="bg-industrial-900 text-blue-400 font-mono">LOW</option>
        </select>

        {/* Date Range Selector */}
        <div className="flex items-center gap-1.5 bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-1 text-xs">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={filters.dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="bg-transparent text-slate-200 text-xs focus:outline-none cursor-pointer font-medium font-mono"
          >
            <option value="7d" className="bg-industrial-900 text-slate-200">Past 7 Days</option>
            <option value="14d" className="bg-industrial-900 text-slate-200">Past 14 Days</option>
            <option value="30d" className="bg-industrial-900 text-slate-200">Past 30 Days (Simulation)</option>
          </select>
        </div>

        {/* Reset Filter Button */}
        {(filters.plantId || filters.severity || filters.searchQuery || filters.dateRange !== '30d') && (
          <button
            onClick={resetFilters}
            title="Reset Filters"
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-800/40 text-slate-400 hover:text-white hover:bg-slate-700/60 transition-all text-xs flex items-center gap-1"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline text-[11px]">Clear</span>
          </button>
        )}

        {/* Status indicator */}
        <div className="h-6 w-[1px] bg-slate-800 mx-1" />

        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span className="hidden md:inline">SYSTEM ONLINE</span>
        </div>

        {/* User profile */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white font-mono border border-cyan-400/30">
          YF
        </div>
      </div>
    </header>
  );
};
