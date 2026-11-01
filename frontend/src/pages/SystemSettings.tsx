import React, { useEffect, useState } from 'react';
import {
  Sliders,
  Save,
  RotateCcw,
  RefreshCw,
  Clock,
  ShieldAlert,
  BellRing,
  History,
  FileCheck,
} from 'lucide-react';
import { toast } from 'react-toastify';
import { settingsApi } from '../services/api';
import { Badge } from '../components/ui/Badge';

export const SystemSettings: React.FC = () => {
  const [settings, setSettings] = useState<any>({
    ack_sla_critical_seconds: 300,
    ack_sla_high_seconds: 900,
    ack_sla_medium_seconds: 1800,
    ack_sla_low_seconds: 3600,
    alarm_flood_threshold: 10,
    alarm_flood_window_minutes: 10,
    repeated_unsafe_window_hours: 24,
    repeated_unsafe_min_events: 3,
    nuisance_alarm_min_count: 15,
    nuisance_max_incident_rate: 0.05,
  });

  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const data = await settingsApi.getSettings();
      setSettings(data.settings);
      setAuditLogs(data.audit_logs);
    } catch (err) {
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleChange = (key: string, value: any) => {
    setSettings((prev: any) => ({ ...prev, [key]: value }));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await settingsApi.updateSettings({
        ...settings,
        actor: 'Lead Safety Architect',
      });
      toast.success('Platform SLA thresholds and detection parameters updated.');
      await fetchSettings();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to save settings.';
      toast.error(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">System Governance & Thresholds</h1>
            <Badge label="CONFIGURABLE" variant="info" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Dynamic acknowledgement SLA rules, alarm flood limits, and safety audit history.
          </p>
        </div>

        <button
          onClick={fetchSettings}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-mono transition-all self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Reload Config
        </button>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Settings Form Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Section 1: Acknowledgement SLAs */}
          <div className="glass-panel rounded-xl p-5 border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider font-mono text-white">
                Alarm Acknowledgement SLAs (Seconds)
              </h3>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div>
                <label className="text-slate-300 block mb-1">
                  Critical Alarm SLA (Seconds) <span className="text-red-400">*</span>
                </label>
                <input
                  type="number"
                  min={30}
                  value={settings.ack_sla_critical_seconds}
                  onChange={(e) => handleChange('ack_sla_critical_seconds', parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500 font-mono"
                />
                <span className="text-[10px] text-slate-500">Currently: {settings.ack_sla_critical_seconds}s (5 mins standard)</span>
              </div>

              <div>
                <label className="text-slate-300 block mb-1">
                  High Severity Alarm SLA (Seconds) <span className="text-orange-400">*</span>
                </label>
                <input
                  type="number"
                  min={60}
                  value={settings.ack_sla_high_seconds}
                  onChange={(e) => handleChange('ack_sla_high_seconds', parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500 font-mono"
                />
                <span className="text-[10px] text-slate-500">Currently: {settings.ack_sla_high_seconds}s (15 mins standard)</span>
              </div>

              <div>
                <label className="text-slate-300 block mb-1">
                  Medium Severity Alarm SLA (Seconds) <span className="text-amber-400">*</span>
                </label>
                <input
                  type="number"
                  min={120}
                  value={settings.ack_sla_medium_seconds}
                  onChange={(e) => handleChange('ack_sla_medium_seconds', parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500 font-mono"
                />
                <span className="text-[10px] text-slate-500">Currently: {settings.ack_sla_medium_seconds}s (30 mins standard)</span>
              </div>

              <div>
                <label className="text-slate-300 block mb-1">
                  Low Severity Alarm SLA (Seconds) <span className="text-blue-400">*</span>
                </label>
                <input
                  type="number"
                  min={300}
                  value={settings.ack_sla_low_seconds}
                  onChange={(e) => handleChange('ack_sla_low_seconds', parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500 font-mono"
                />
                <span className="text-[10px] text-slate-500">Currently: {settings.ack_sla_low_seconds}s (60 mins standard)</span>
              </div>
            </div>
          </div>

          {/* Section 2: Anomaly Detection Thresholds */}
          <div className="glass-panel rounded-xl p-5 border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
              <ShieldAlert className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider font-mono text-white">
                Intelligence Detection Parameters
              </h3>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-300 block mb-1">Alarm Flood Count</label>
                  <input
                    type="number"
                    min={5}
                    value={settings.alarm_flood_threshold}
                    onChange={(e) => handleChange('alarm_flood_threshold', parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500"
                  />
                  <span className="text-[10px] text-slate-500">Min alarms trigger</span>
                </div>
                <div>
                  <label className="text-slate-300 block mb-1">Flood Window (Mins)</label>
                  <input
                    type="number"
                    min={1}
                    value={settings.alarm_flood_window_minutes}
                    onChange={(e) => handleChange('alarm_flood_window_minutes', parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500"
                  />
                  <span className="text-[10px] text-slate-500">ISA-18.2 burst window</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-300 block mb-1">Repeated Unsafe Min Events</label>
                  <input
                    type="number"
                    min={2}
                    value={settings.repeated_unsafe_min_events}
                    onChange={(e) => handleChange('repeated_unsafe_min_events', parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500"
                  />
                  <span className="text-[10px] text-slate-500">Critical events count</span>
                </div>
                <div>
                  <label className="text-slate-300 block mb-1">Rolling Window (Hours)</label>
                  <input
                    type="number"
                    min={1}
                    value={settings.repeated_unsafe_window_hours}
                    onChange={(e) => handleChange('repeated_unsafe_window_hours', parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500"
                  />
                  <span className="text-[10px] text-slate-500">Evaluation lookback</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-300 block mb-1">Nuisance Min Triggers</label>
                  <input
                    type="number"
                    min={5}
                    value={settings.nuisance_alarm_min_count}
                    onChange={(e) => handleChange('nuisance_alarm_min_count', parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500"
                  />
                  <span className="text-[10px] text-slate-500">Chattering frequency</span>
                </div>
                <div>
                  <label className="text-slate-300 block mb-1">Max Incident Rate</label>
                  <input
                    type="number"
                    step={0.01}
                    min={0.01}
                    max={0.5}
                    value={settings.nuisance_max_incident_rate}
                    onChange={(e) => handleChange('nuisance_max_incident_rate', parseFloat(e.target.value) || 0.05)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500"
                  />
                  <span className="text-[10px] text-slate-500">Incident conversion cutoff</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono font-bold text-xs shadow-lg transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Applying Configuration...' : 'Save & Enforce Thresholds'}
          </button>
        </div>
      </form>

      {/* Audit History Log */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-semibold uppercase font-mono tracking-wider text-white">
              System Configuration & Verification Audit Trail
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">{auditLogs.length} Logged Audit Events</span>
        </div>

        <div className="overflow-x-auto max-h-64">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] border-b border-slate-800 sticky top-0">
              <tr>
                <th className="py-2.5 px-4">Entity</th>
                <th className="py-2.5 px-4">Entity ID</th>
                <th className="py-2.5 px-4">Action</th>
                <th className="py-2.5 px-4">Authorized Actor</th>
                <th className="py-2.5 px-4">Details</th>
                <th className="py-2.5 px-4 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-industrial-950/40">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-4 text-cyan-400 font-bold">{log.entity_name}</td>
                  <td className="py-2.5 px-4 text-slate-300">{log.entity_id}</td>
                  <td className="py-2.5 px-4">
                    <Badge label={log.action} size="sm" />
                  </td>
                  <td className="py-2.5 px-4 text-slate-200 font-sans">{log.actor}</td>
                  <td className="py-2.5 px-4 text-slate-400 font-sans truncate max-w-sm">{log.details}</td>
                  <td className="py-2.5 px-4 text-right text-slate-500 text-[11px]">
                    {log.timestamp.slice(0, 19).replace('T', ' ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
