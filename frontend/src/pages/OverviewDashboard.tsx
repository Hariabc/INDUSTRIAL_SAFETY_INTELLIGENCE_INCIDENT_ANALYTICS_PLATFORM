import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Factory,
  Cpu,
  BellRing,
  AlertOctagon,
  AlertTriangle,
  CheckSquare,
  ShieldCheck,
  TrendingUp,
  ArrowUpRight,
  RefreshCw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
  BarChart,
  Bar,
} from 'recharts';
import { dashboardApi, analyticsApi } from '../services/api';
import { OverviewStats } from '../types';
import { StatCard } from '../components/ui/StatCard';
import { Badge } from '../components/ui/Badge';
import { useFilters } from '../context/FilterContext';

export const OverviewDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { filters } = useFilters();
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [recentAlarms, setRecentAlarms] = useState<any[]>([]);
  const [recentIncidents, setRecentIncidents] = useState<any[]>([]);
  const [alarmTrends, setAlarmTrends] = useState<any[]>([]);
  const [severityDist, setSeverityDist] = useState<any[]>([]);
  const [unsafeMachines, setUnsafeMachines] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [dashData, trends, sevData, unsafe] = await Promise.all([
        dashboardApi.getOverview(),
        analyticsApi.getAlarmTrends({ plant_id: filters.plantId || undefined }),
        analyticsApi.getSeverityDistribution({ plant_id: filters.plantId || undefined }),
        analyticsApi.getUnsafeMachines(6),
      ]);

      setStats(dashData.stats);
      setRecentAlarms(dashData.recent_critical_alarms);
      setRecentIncidents(dashData.recent_incidents);
      setAlarmTrends(trends);
      setSeverityDist(sevData);
      setUnsafeMachines(unsafe);
    } catch (err) {
      console.error('Error loading dashboard overview:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters.plantId]);

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
          <p className="text-sm font-mono text-slate-400">Loading Industrial Safety Telemetry...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Executive Safety Overview</h1>
            <Badge label="REAL-TIME" variant="info" dot />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Enterprise Industrial Safety Intelligence, Machine States, and Anomaly Telemetry.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-mono transition-all self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Metrics
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        <div className="col-span-2">
          <StatCard
            title="Total Plants"
            value={stats?.total_plants || 4}
            subtitle="Global manufacturing sites"
            icon={Factory}
            variant="cyan"
          />
        </div>
        <div className="col-span-2">
          <StatCard
            title="Monitored Machines"
            value={stats?.total_machines || 60}
            subtitle="Critical equipment assets"
            icon={Cpu}
            variant="blue"
          />
        </div>
        <div className="col-span-2">
          <StatCard
            title="Total Alarms"
            value={(stats?.total_alarms || 50035).toLocaleString()}
            subtitle="30-day historical events"
            icon={BellRing}
            variant="slate"
          />
        </div>
        <div className="col-span-2">
          <StatCard
            title="Critical Alarms"
            value={(stats?.critical_alarms || 0).toLocaleString()}
            subtitle="Immediate response required"
            icon={AlertOctagon}
            variant="red"
          />
        </div>
        <div className="col-span-2">
          <StatCard
            title="Active Incidents"
            value={stats?.active_incidents || 0}
            subtitle="Open or investigating"
            icon={AlertTriangle}
            variant="orange"
          />
        </div>
        <div className="col-span-2">
          <StatCard
            title="Pending Actions"
            value={stats?.unresolved_corrective_actions || 0}
            subtitle="Unresolved corrective actions"
            icon={CheckSquare}
            variant="amber"
          />
        </div>
        <div className="col-span-2">
          <StatCard
            title="Safety Score"
            value={`${stats?.plant_safety_score || 93.2}%`}
            subtitle="Enterprise safety index"
            icon={ShieldCheck}
            variant="emerald"
            trend={{ value: '+1.4%', isPositive: true }}
          />
        </div>
        <div className="col-span-2">
          <StatCard
            title="Data Integrity"
            value={`${stats?.data_integrity_score || 100}%`}
            subtitle="10-check validation score"
            icon={TrendingUp}
            variant="cyan"
          />
        </div>
      </div>

      {/* Main Analytical Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alarm Trend Over Time (2 cols) */}
        <div className="lg:col-span-2 glass-panel rounded-xl p-5 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white tracking-wide">Alarm Frequencies Over Time</h3>
              <p className="text-xs text-slate-400">Daily alarm volumes across severity classifications</p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="flex items-center gap-1.5 text-red-400">
                <span className="w-2 h-2 rounded-full bg-red-500" /> Critical
              </span>
              <span className="flex items-center gap-1.5 text-orange-400">
                <span className="w-2 h-2 rounded-full bg-orange-500" /> High
              </span>
              <span className="flex items-center gap-1.5 text-amber-400">
                <span className="w-2 h-2 rounded-full bg-amber-500" /> Medium
              </span>
              <span className="flex items-center gap-1.5 text-blue-400">
                <span className="w-2 h-2 rounded-full bg-blue-500" /> Low
              </span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={alarmTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCrit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: '#94a3b8', fontSize: 10 }}
                  tickFormatter={(val) => val.slice(5)}
                />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#f8fafc',
                  }}
                />
                <Area type="monotone" dataKey="CRITICAL" stroke="#ef4444" fillOpacity={1} fill="url(#colorCrit)" />
                <Area type="monotone" dataKey="HIGH" stroke="#f97316" fillOpacity={1} fill="url(#colorHigh)" />
                <Area type="monotone" dataKey="MEDIUM" stroke="#eab308" fillOpacity={0.1} fill="#eab308" />
                <Area type="monotone" dataKey="LOW" stroke="#3b82f6" fillOpacity={0.1} fill="#3b82f6" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution Donut */}
        <div className="glass-panel rounded-xl p-5 border border-slate-800">
          <h3 className="text-sm font-semibold text-white tracking-wide">Severity Distribution</h3>
          <p className="text-xs text-slate-400 mb-4">Total alarm volume proportion by criticality tier</p>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityDist}
                  dataKey="count"
                  nameKey="severity"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                >
                  {severityDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 mt-2">
            {severityDist.map((item) => (
              <div key={item.severity} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="font-mono text-slate-300">{item.severity}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-slate-400">{item.count.toLocaleString()}</span>
                  <span className="font-mono font-medium text-white w-12 text-right">{item.percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Second Row: Top Unsafe Machines & High-Priority Incidents */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Machines with Repeated Unsafe Conditions */}
        <div className="glass-panel rounded-xl p-5 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white tracking-wide">
                Top Equipment with Unsafe Conditions
              </h3>
              <p className="text-xs text-slate-400">Assets exhibiting repeated trips and safety alarm clusters</p>
            </div>
            <button
              onClick={() => navigate('/machines')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-mono"
            >
              View All <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[11px] font-mono uppercase text-slate-400 border-b border-slate-800 bg-slate-900/50">
                <tr>
                  <th className="py-2.5 px-3">Machine</th>
                  <th className="py-2.5 px-3">Plant</th>
                  <th className="py-2.5 px-3">State</th>
                  <th className="py-2.5 px-3 text-right">Critical Alarms</th>
                  <th className="py-2.5 px-3 text-right">Incidents</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {unsafeMachines.map((m) => (
                  <tr
                    key={m.machine_id}
                    onClick={() => navigate(`/machines?search=${m.machine_id}`)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-3 font-semibold text-cyan-400">{m.machine_id}</td>
                    <td className="py-2.5 px-3 text-slate-300">{m.plant_name.split(' ')[0]}</td>
                    <td className="py-2.5 px-3">
                      <Badge label={m.current_state} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-red-400">{m.critical_alarms}</td>
                    <td className="py-2.5 px-3 text-right font-bold text-amber-400">{m.incident_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* High-Priority Active Incidents */}
        <div className="glass-panel rounded-xl p-5 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white tracking-wide">
                High-Priority Incident Log
              </h3>
              <p className="text-xs text-slate-400">Active safety events requiring root-cause investigation</p>
            </div>
            <button
              onClick={() => navigate('/incidents')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-mono"
            >
              All Incidents <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2.5">
            {recentIncidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => navigate(`/incidents?search=${inc.id}`)}
                className="p-3 rounded-lg border border-slate-800 bg-slate-900/40 hover:bg-slate-800/60 hover:border-slate-700 transition-all cursor-pointer flex items-center justify-between gap-4"
              >
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-cyan-400">{inc.id}</span>
                    <Badge label={inc.severity} size="sm" />
                    <Badge label={inc.status} size="sm" />
                  </div>
                  <p className="text-xs text-slate-200 truncate">{inc.title}</p>
                  <p className="text-[10px] font-mono text-slate-500">
                    Machine: {inc.machine_id} | Type: {inc.incident_type}
                  </p>
                </div>
                <div className="text-right text-[11px] font-mono text-slate-400 whitespace-nowrap">
                  {inc.timestamp.slice(0, 10)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
