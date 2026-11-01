import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'red' | 'orange' | 'amber' | 'blue' | 'emerald' | 'cyan' | 'slate';
  trend?: {
    value: string;
    isPositive?: boolean;
  };
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'cyan',
  trend,
}) => {
  const borderVariants = {
    red: 'border-l-4 border-l-red-500 hover:border-red-500/50',
    orange: 'border-l-4 border-l-orange-500 hover:border-orange-500/50',
    amber: 'border-l-4 border-l-amber-500 hover:border-amber-500/50',
    blue: 'border-l-4 border-l-blue-500 hover:border-blue-500/50',
    emerald: 'border-l-4 border-l-emerald-500 hover:border-emerald-500/50',
    cyan: 'border-l-4 border-l-cyan-500 hover:border-cyan-500/50',
    slate: 'border-l-4 border-l-slate-500 hover:border-slate-500/50',
  }[variant];

  const iconColors = {
    red: 'text-red-400 bg-red-500/10',
    orange: 'text-orange-400 bg-orange-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
    blue: 'text-blue-400 bg-blue-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    cyan: 'text-cyan-400 bg-cyan-500/10',
    slate: 'text-slate-400 bg-slate-500/10',
  }[variant];

  return (
    <div
      className={`glass-panel rounded-lg p-4 transition-all duration-200 hover:translate-y-[-2px] ${borderVariants}`}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
        <div className={`p-2 rounded-md ${iconColors}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <h3 className="text-2xl font-bold font-mono tracking-tight text-white">{value}</h3>
        {trend && (
          <span
            className={`text-xs font-mono font-medium ${
              trend.isPositive ? 'text-emerald-400' : 'text-red-400'
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
};
