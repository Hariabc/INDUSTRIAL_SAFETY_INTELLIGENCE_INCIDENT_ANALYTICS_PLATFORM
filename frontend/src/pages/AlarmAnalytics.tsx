import React, { useEffect, useState } from 'react';
import {
  BellRing,
  AlertOctagon,
  Clock,
  Layers,
  Search,
  Filter,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { alarmsApi, analyticsApi } from '../services/api';
import { AlarmEvent } from '../types';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { useFilters } from '../context/FilterContext';

export const AlarmAnalytics: React.FC = () => {
  const { filters } = useFilters();
  const [alarms, setAlarms] = useState<AlarmEvent[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [nuisanceOnly, setNuisanceOnly] = useState<boolean>(false);

  const [trendData, setTrendData] = useState<any[]>([]);
  const [sevDist, setSevDist] = useState<any[]>([]);
  const [ackPerformance, setAckPerformance] = useState<any | null>(null);

  const [selectedAlarmId, setSelectedAlarmId] = useState<string | null>(null);
  const [alarmDetail, setAlarmDetail] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [alarmRes, trends, dist, ackPerf] = await Promise.all([
        alarmsApi.getAll({
          plant_id: filters.plantId || undefined,
          machine_id: filters.machineId || undefined,
          severity: severityFilter || filters.severity || undefined,
          status: statusFilter || undefined,
          is_nuisance: nuisanceOnly ? true : undefined,
          search: filters.searchQuery || undefined,
          page,
          page_size: 20,
        }),
        analyticsApi.getAlarmTrends({ plant_id: filters.plantId || undefined }),
        analyticsApi.getSeverityDistribution({ plant_id: filters.plantId || undefined }),
        analyticsApi.getAcknowledgementPerformance(filters.plantId || undefined),
      ]);

      setAlarms(alarmRes.items);
      setTotal(alarmRes.total);
      setTotalPages(alarmRes.total_pages);
      setTrendData(trends);
      setSevDist(dist);
      setAckPerformance(ackPerf);
    } catch (err) {
      console.error('Error fetching alarm analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters.plantId, filters.machineId, filters.severity, filters.searchQuery, severityFilter, statusFilter, nuisanceOnly, page]);

  const handleOpenDetail = async (id: string) => {
    try {
      setSelectedAlarmId(id);
      setDetailLoading(true);
      const detail = await alarmsApi.getById(id);
      setAlarmDetail(detail);
    } catch (err) {
      console.error('Error fetching alarm detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Alarm Analytics & Telemetry</h1>
            <Badge label={`${total.toLocaleString()} EVENTS`} variant="info" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Severity tiers, acknowledgement delay distributions, flood detection, and chattering patterns.
          </p>
        </div>

        {/* Local Filter Bar */}
        <div className="flex items-center gap-3 self-start">
          <select
            value={severityFilter}
            onChange={(e) => {
              setSeverityFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          <label className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-xs text-slate-300 cursor-pointer font-mono select-none">
            <input
              type="checkbox"
              checked={nuisanceOnly}
              onChange={(e) => {
                setNuisanceOnly(e.target.checked);
                setPage(1);
              }}
              className="rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0"
            />
            Nuisance Only
          </label>

          <button
            onClick={fetchData}
            className="p-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Analytics KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
        <div className="glass-panel p-4 rounded-xl border border-slate-800">
          <span className="text-slate-400 text-xs">Total Alarms</span>
          <p className="text-xl font-bold text-white mt-1">{total.toLocaleString()}</p>
          <span className="text-[11px] text-slate-500 mt-1 block">Full simulation volume</span>
        </div>
        <div className="glass-panel p-4 rounded-xl border border-slate-800">
          <span className="text-slate-400 text-xs">Avg Ack Response</span>
          <p className="text-xl font-bold text-cyan-400 mt-1">
            {ackPerformance?.average_ack_time_seconds || 785}s
          </p>
          <span className="text-[11px] text-slate-500 mt-1 block">Mean operator latency</span>
        </div>
        <div className="glass-panel p-4 rounded-xl border border-slate-800">
          <span className="text-slate-400 text-xs">SLA Compliance</span>
          <p className="text-xl font-bold text-emerald-400 mt-1">
            {ackPerformance?.sla_adherence_rate || 85.3}%
          </p>
          <span className="text-[11px] text-slate-500 mt-1 block">Within catalog SLA threshold</span>
        </div>
        <div className="glass-panel p-4 rounded-xl border border-slate-800">
          <span className="text-slate-400 text-xs">Delayed Acknowledgements</span>
          <p className="text-xl font-bold text-amber-400 mt-1">
            {ackPerformance?.delayed_rate || 14.7}%
          </p>
          <span className="text-[11px] text-slate-500 mt-1 block">Exceeded response SLA</span>
        </div>
      </div>

      {/* Visual Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel rounded-xl p-5 border border-slate-800">
          <h3 className="text-sm font-semibold text-white tracking-wide mb-1">Alarm Volumes Timeline</h3>
          <p className="text-xs text-slate-400 mb-4">Historical daily alarm distribution</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 10 }} tickFormatter={(d) => d.slice(5)} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Area type="monotone" dataKey="CRITICAL" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
                <Area type="monotone" dataKey="HIGH" stroke="#f97316" fill="#f97316" fillOpacity={0.2} />
                <Area type="monotone" dataKey="MEDIUM" stroke="#eab308" fill="#eab308" fillOpacity={0.1} />
                <Area type="monotone" dataKey="LOW" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel rounded-xl p-5 border border-slate-800">
          <h3 className="text-sm font-semibold text-white tracking-wide mb-1">Severity Breakdown</h3>
          <p className="text-xs text-slate-400 mb-4">Percentage of total alarm events</p>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sevDist} dataKey="count" nameKey="severity" innerRadius={45} outerRadius={70}>
                  {sevDist.map((e, idx) => (
                    <Cell key={idx} fill={e.color} />
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
          <div className="space-y-1.5 mt-2 font-mono text-xs">
            {sevDist.map((d) => (
              <div key={d.severity} className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-slate-300">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }} />
                  {d.severity}
                </span>
                <span className="text-white font-bold">{d.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alarm Log Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Alarm ID</th>
                <th className="py-3 px-4">Machine</th>
                <th className="py-3 px-4">Plant</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Source Event Fingerprint</th>
                <th className="py-3 px-4">Telemetry Metric</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-industrial-950/40">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mx-auto mb-2" />
                    Querying alarm telemetry...
                  </td>
                </tr>
              ) : alarms.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    No alarm records found for the applied parameters.
                  </td>
                </tr>
              ) : (
                alarms.map((a) => (
                  <tr
                    key={a.id}
                    onClick={() => handleOpenDetail(a.id)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-bold text-cyan-400 group-hover:underline">
                      {a.id}
                    </td>
                    <td className="py-3 px-4 text-slate-200">{a.machine_id}</td>
                    <td className="py-3 px-4 text-slate-400">{a.plant_id}</td>
                    <td className="py-3 px-4">
                      <Badge label={a.severity} size="sm" dot={a.severity === 'CRITICAL'} />
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px] truncate max-w-xs">
                      {a.source_event_id}
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      {a.value ? `${a.value} ${a.unit || ''}` : 'Discrete Trip'}
                    </td>
                    <td className="py-3 px-4">
                      <Badge label={a.is_nuisance ? 'NUISANCE' : a.status} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-right text-slate-500 text-[11px]">
                      {a.event_timestamp.slice(0, 19).replace('T', ' ')}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800 bg-slate-900/60 text-xs font-mono text-slate-400">
          <div>
            Showing Page <span className="text-white font-bold">{page}</span> of{' '}
            <span className="text-white font-bold">{totalPages}</span> ({total.toLocaleString()} Records)
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded border border-slate-800 bg-slate-800/50 hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed text-white"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 rounded border border-slate-800 bg-slate-800/50 hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed text-white"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Alarm Detail Modal */}
      <Modal
        isOpen={!!selectedAlarmId}
        onClose={() => setSelectedAlarmId(null)}
        title={`Alarm Telemetry: ${selectedAlarmId}`}
        subtitle={`Specification Code: ${alarmDetail?.definition.code || ''} | Category: ${alarmDetail?.definition.category || ''}`}
        maxWidth="2xl"
      >
        {detailLoading ? (
          <div className="flex items-center justify-center p-12">
            <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin" />
          </div>
        ) : alarmDetail ? (
          <div className="space-y-5 font-mono text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Severity</span>
                <div className="mt-1">
                  <Badge label={alarmDetail.alarm.severity} dot />
                </div>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Machine Asset</span>
                <p className="text-white font-bold mt-1">{alarmDetail.machine.name} ({alarmDetail.machine.id})</p>
              </div>
            </div>

            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-2">
              <span className="text-slate-400 font-bold uppercase text-[10px]">Catalog Definition</span>
              <p className="text-white font-medium text-sm">{alarmDetail.definition.name}</p>
              <p className="text-slate-400 font-sans">{alarmDetail.definition.description || 'Standard safety violation limit.'}</p>
              <p className="text-cyan-400 text-[11px]">SLA Response Threshold: {alarmDetail.definition.ack_sla_seconds} seconds</p>
            </div>

            {/* Acknowledgement Info */}
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-2">
              <span className="text-slate-400 font-bold uppercase text-[10px]">Operator Acknowledgement</span>
              {alarmDetail.acknowledgement ? (
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-300">Responding Operator:</span>
                    <span className="text-white font-semibold">{alarmDetail.acknowledgement.operator_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Response Delay:</span>
                    <span className="text-cyan-400 font-bold">{alarmDetail.acknowledgement.ack_delay_seconds}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">SLA Status:</span>
                    <Badge label={alarmDetail.acknowledgement.sla_status} size="sm" />
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Operator Notes:</span>
                    <span className="text-slate-300 font-sans italic">{alarmDetail.acknowledgement.notes || 'None'}</span>
                  </div>
                </div>
              ) : (
                <p className="text-amber-400">Pending operator acknowledgement.</p>
              )}
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};
