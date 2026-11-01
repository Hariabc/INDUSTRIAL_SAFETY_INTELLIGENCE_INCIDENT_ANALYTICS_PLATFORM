import React, { useEffect, useState } from 'react';
import {
  Cpu,
  Search,
  Filter,
  RefreshCw,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  Clock,
  Activity,
  Lock,
} from 'lucide-react';
import { machinesApi } from '../services/api';
import { Machine, MachineDetail } from '../types';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { useFilters } from '../context/FilterContext';

export const MachineMonitoring: React.FC = () => {
  const { filters, setPlantId } = useFilters();
  const [machines, setMachines] = useState<Machine[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [stateFilter, setStateFilter] = useState<string>('');
  const [critFilter, setCritFilter] = useState<string>('');

  const [selectedMachineId, setSelectedMachineId] = useState<string | null>(null);
  const [machineDetail, setMachineDetail] = useState<MachineDetail | null>(null);
  const [machineHistory, setMachineHistory] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  const fetchMachines = async () => {
    try {
      setLoading(true);
      const data = await machinesApi.getAll({
        plant_id: filters.plantId || undefined,
        state: stateFilter || undefined,
        criticality: critFilter || filters.severity || undefined,
        search: filters.searchQuery || undefined,
        page,
        page_size: 15,
      });

      setMachines(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching machines:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMachines();
  }, [filters.plantId, filters.severity, filters.searchQuery, stateFilter, critFilter, page]);

  const handleOpenDetail = async (mId: string) => {
    try {
      setSelectedMachineId(mId);
      setDetailLoading(true);
      const [detail, history] = await Promise.all([
        machinesApi.getById(mId),
        machinesApi.getHistory(mId),
      ]);
      setMachineDetail(detail);
      setMachineHistory(history);
    } catch (err) {
      console.error('Error fetching machine details:', err);
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
            <h1 className="text-2xl font-bold tracking-tight text-white">Machine Monitoring</h1>
            <Badge label={`${total} UNITS`} variant="info" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time machine states, safety interlocks, and historical transition telemetry.
          </p>
        </div>

        {/* Local Filter Bar */}
        <div className="flex items-center gap-3 self-start">
          <select
            value={stateFilter}
            onChange={(e) => {
              setStateFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
          >
            <option value="">All States</option>
            <option value="RUNNING">RUNNING</option>
            <option value="IDLE">IDLE</option>
            <option value="TRIPPED">TRIPPED</option>
            <option value="EMERGENCY_STOP">EMERGENCY STOP</option>
            <option value="MAINTENANCE">MAINTENANCE</option>
            <option value="UNSAFE">UNSAFE</option>
          </select>

          <select
            value={critFilter}
            onChange={(e) => {
              setCritFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
          >
            <option value="">All Criticality</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          <button
            onClick={fetchMachines}
            className="p-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Machines Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Machine ID</th>
                <th className="py-3 px-4">Asset Name</th>
                <th className="py-3 px-4">Plant Site</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Current State</th>
                <th className="py-3 px-4">Criticality</th>
                <th className="py-3 px-4 text-right">Alarms</th>
                <th className="py-3 px-4 text-right">Incidents</th>
                <th className="py-3 px-4 text-right">Last Telemetry</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-industrial-950/40">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mx-auto mb-2" />
                    Fetching machine telemetry...
                  </td>
                </tr>
              ) : machines.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    No machinery matches the selected filter parameters.
                  </td>
                </tr>
              ) : (
                machines.map((m) => (
                  <tr
                    key={m.id}
                    onClick={() => handleOpenDetail(m.id)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-bold text-cyan-400 group-hover:underline">
                      {m.id}
                    </td>
                    <td className="py-3 px-4 text-slate-200 font-sans font-medium">{m.name}</td>
                    <td className="py-3 px-4 text-slate-400">{m.plant_name?.split(' ')[0]}</td>
                    <td className="py-3 px-4 text-slate-400">{m.type}</td>
                    <td className="py-3 px-4">
                      <Badge label={m.current_state} size="sm" dot />
                    </td>
                    <td className="py-3 px-4">
                      <Badge label={m.criticality} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-slate-200">
                      {(m.alarm_count || 0).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-amber-400">
                      {m.incident_count || 0}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-500 text-[11px]">
                      {m.last_event_timestamp ? m.last_event_timestamp.slice(0, 16).replace('T', ' ') : 'N/A'}
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
            <span className="text-white font-bold">{totalPages}</span> ({total} Machines)
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

      {/* Machine Detail Modal */}
      <Modal
        isOpen={!!selectedMachineId}
        onClose={() => setSelectedMachineId(null)}
        title={machineDetail?.machine.name || 'Machine Monitoring Details'}
        subtitle={`Asset ID: ${selectedMachineId} | Type: ${machineDetail?.machine.type || ''} | Model: ${machineDetail?.machine.model_number || ''}`}
        maxWidth="4xl"
      >
        {detailLoading ? (
          <div className="flex items-center justify-center p-12">
            <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin" />
          </div>
        ) : machineDetail ? (
          <div className="space-y-6">
            {/* Top Stat Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs">Current State</span>
                <div className="mt-1">
                  <Badge label={machineDetail.machine.current_state} dot />
                </div>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs">Total Alarms</span>
                <p className="text-lg font-bold text-white mt-0.5">
                  {machineDetail.stats.total_alarms.toLocaleString()}
                </p>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs">Critical Alarms</span>
                <p className="text-lg font-bold text-red-400 mt-0.5">
                  {machineDetail.stats.critical_alarms}
                </p>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs">Safety Incidents</span>
                <p className="text-lg font-bold text-amber-400 mt-0.5">
                  {machineDetail.stats.incidents}
                </p>
              </div>
            </div>

            {/* Safety Interlocks Section */}
            <div>
              <h4 className="text-xs font-semibold uppercase font-mono tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                <Lock className="w-4 h-4 text-cyan-400" /> Dedicated Safety Interlocks ({machineDetail.interlocks.length})
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {machineDetail.interlocks.map((itl) => (
                  <div key={itl.id} className="p-3 rounded-lg border border-slate-800 bg-slate-950/60">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs text-cyan-400 font-bold">{itl.id}</span>
                      <Badge label={itl.current_state} size="sm" />
                    </div>
                    <p className="text-xs font-medium text-white mt-1">{itl.name}</p>
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mt-2">
                      <span>Type: {itl.interlock_type}</span>
                      <span>Target: {itl.target_state}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Machine State Transition History */}
            <div>
              <h4 className="text-xs font-semibold uppercase font-mono tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4 text-amber-400" /> Historical State Transitions (Append-Only Log)
              </h4>
              <div className="border border-slate-800 rounded-lg overflow-x-auto max-h-52">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] sticky top-0">
                    <tr>
                      <th className="p-2.5">Timestamp</th>
                      <th className="p-2.5">From</th>
                      <th className="p-2.5">To</th>
                      <th className="p-2.5">Transition Trigger</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 bg-slate-950/40">
                    {machineHistory?.state_transitions?.map((st: any) => (
                      <tr key={st.id} className="hover:bg-slate-900/50">
                        <td className="p-2.5 text-slate-400 whitespace-nowrap">
                          {st.timestamp.slice(0, 19).replace('T', ' ')}
                        </td>
                        <td className="p-2.5 text-slate-400">{st.previous_state || 'INITIAL'}</td>
                        <td className="p-2.5">
                          <Badge label={st.new_state} size="sm" />
                        </td>
                        <td className="p-2.5 text-slate-200">{st.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};
