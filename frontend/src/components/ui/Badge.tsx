import React from 'react';

interface BadgeProps {
  label: string;
  variant?: 'critical' | 'high' | 'medium' | 'low' | 'info' | 'success' | 'warning' | 'neutral';
  size?: 'sm' | 'md';
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  variant = 'neutral',
  size = 'md',
  dot = false,
}) => {
  const normalized = label ? label.toUpperCase() : 'UNKNOWN';

  let autoVariant = variant;
  if (['CRITICAL', 'EMERGENCY_STOP', 'UNSAFE', 'FAILED', 'ANOMALOUS_PRE_ALARM', 'FAULT'].includes(normalized)) {
    autoVariant = 'critical';
  } else if (['HIGH', 'TRIPPED', 'DELAYED', 'BYPASSED'].includes(normalized)) {
    autoVariant = 'high';
  } else if (['MEDIUM', 'WARNING', 'INVESTIGATING', 'IN_PROGRESS'].includes(normalized)) {
    autoVariant = 'medium';
  } else if (['LOW', 'IDLE', 'CONTAINED'].includes(normalized)) {
    autoVariant = 'low';
  } else if (['ACTIVE', 'RUNNING', 'COMPLETED', 'CLOSED', 'RESOLVED', 'WITHIN_SLA', 'PASSED', 'ENGAGED'].includes(normalized)) {
    autoVariant = 'success';
  }

  const colorStyles = {
    critical: 'bg-red-500/15 text-red-400 border-red-500/30',
    high: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
    medium: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    low: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    info: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    warning: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
    neutral: 'bg-slate-700/30 text-slate-300 border-slate-600/30',
  }[autoVariant];

  const dotColors = {
    critical: 'bg-red-400',
    high: 'bg-orange-400',
    medium: 'bg-amber-400',
    low: 'bg-blue-400',
    info: 'bg-cyan-400',
    success: 'bg-emerald-400',
    warning: 'bg-yellow-400',
    neutral: 'bg-slate-400',
  }[autoVariant];

  const sizeStyles = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-medium rounded-md border ${colorStyles} ${sizeStyles}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dotColors} animate-pulse`} />}
      {label}
    </span>
  );
};
