import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Factory,
  Cpu,
  BellRing,
  ShieldAlert,
  AlertTriangle,
  CheckSquare,
  Database,
  Sliders,
  Activity,
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/plants', label: 'Plant Monitoring', icon: Factory },
  { path: '/machines', label: 'Machine Monitoring', icon: Cpu },
  { path: '/alarms', label: 'Alarm Analytics', icon: BellRing },
  { path: '/safety', label: 'Safety Intelligence', icon: ShieldAlert, badge: 'AI' },
  { path: '/incidents', label: 'Incident Management', icon: AlertTriangle },
  { path: '/actions', label: 'Corrective Actions', icon: CheckSquare },
  { path: '/data-quality', label: 'Data Quality', icon: Database },
  { path: '/settings', label: 'System Settings', icon: Sliders },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-industrial-900 border-r border-slate-800 flex flex-col h-screen fixed left-0 top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center glow-cyan shadow-lg">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-wide text-white leading-tight">SAFETY INTEL</h1>
          <p className="text-[10px] text-cyan-400 font-mono tracking-widest uppercase">YottaFlex.ai</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-mono uppercase tracking-wider text-slate-500">
          Navigation Modules
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all group ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 transition-transform group-hover:scale-110" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-800 bg-industrial-950/40">
        <div className="glass-panel rounded-lg p-3">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-slate-400 font-medium">Detection Engine</span>
            <span className="inline-flex items-center gap-1 font-mono text-[11px] text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              ACTIVE
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-1.5 rounded-full w-full" />
          </div>
          <p className="text-[10px] text-slate-500 mt-2 font-mono">Precision: 100% | SLA: 98.4%</p>
        </div>
      </div>
    </aside>
  );
};
