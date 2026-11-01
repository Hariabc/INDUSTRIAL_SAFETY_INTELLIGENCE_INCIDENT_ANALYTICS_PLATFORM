import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Search,
  Filter,
  RefreshCw,
  Clock,
  User,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  CheckCircle,
  FileText,
} from 'lucide-react';
import { toast } from 'react-toastify';
import { incidentsApi } from '../services/api';
import { Incident, IncidentDetail } from '../types';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { useFilters } from '../context/FilterContext';

export const IncidentManagement: React.FC = () => {
  const { filters } = useFilters();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [sevFilter, setSevFilter] = useState<string>('');

  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [incidentDetail, setIncidentDetail] = useState<IncidentDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);
  const [advancingStatus, setAdvancingStatus] = useState<boolean>(false);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const data = await incidentsApi.getAll({
        plant_id: filters.plantId || undefined,
        machine_id: filters.machineId || undefined,
        severity: sevFilter || filters.severity || undefined,
        status: statusFilter || undefined,
        incident_type: typeFilter || undefined,
        search: filters.searchQuery || undefined,
        page,
        page_size: 15,
      });

      setIncidents(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [filters.plantId, filters.machineId, filters.severity, filters.searchQuery, statusFilter, typeFilter, sevFilter, page]);

  const handleOpenDetail = async (id: string) => {
    try {
      setSelectedIncidentId(id);
      setDetailLoading(true);
      const detail = await incidentsApi.getById(id);
      setIncidentDetail(detail);
    } catch (err) {
      console.error('Error fetching incident detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleAdvanceStatus = async (nextStatus: string) => {
    if (!selectedIncidentId) return;
    try {
      setAdvancingStatus(true);
      await incidentsApi.acknowledge(selectedIncidentId, nextStatus);
      toast.success(`Incident ${selectedIncidentId} progressed to ${nextStatus}`);
      const updated = await incidentsApi.getById(selectedIncidentId);
      setIncidentDetail(updated);
      await fetchIncidents();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to update incident status.';
      toast.error(msg);
    } finally {
      setAdvancingStatus(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Incident Management & RCA</h1>
            <Badge label={`${total} INCIDENTS`} variant="high" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            End-to-end incident traceability, root-cause correlation, and authentic chronological timelines.
          </p>
        </div>

        {/* Local Filter Bar */}
        <div className="flex items-center gap-3 self-start">
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">OPEN</option>
            <option value="INVESTIGATING">INVESTIGATING</option>
            <option value="CONTAINED">CONTAINED</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="CLOSED">CLOSED</option>
          </select>

          <select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
          >
            <option value="">All Incident Types</option>
            <option value="INTERLOCK_FAILURE">Interlock Failure</option>
            <option value="SAFETY_BREACH">Safety Breach</option>
            <option value="EQUIPMENT_DAMAGE">Equipment Damage</option>
            <option value="NEAR_MISS">Near Miss</option>
            <option value="HAZARDOUS_RELEASE">Hazardous Release</option>
          </select>

          <button
            onClick={fetchIncidents}
            className="p-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Incident ID</th>
                <th className="py-3 px-4">Incident Title</th>
                <th className="py-3 px-4">Plant</th>
                <th className="py-3 px-4">Machine</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Investigator</th>
                <th className="py-3 px-4 text-right">Inception Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-industrial-950/40">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mx-auto mb-2" />
                    Loading safety incidents...
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    No safety incidents found matching the selected filter criteria.
                  </td>
                </tr>
              ) : (
                incidents.map((inc) => (
                  <tr
                    key={inc.id}
                    onClick={() => handleOpenDetail(inc.id)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-bold text-cyan-400 group-hover:underline">
                      {inc.id}
                    </td>
                    <td className="py-3 px-4 text-slate-200 font-sans font-medium truncate max-w-xs">
                      {inc.title}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{inc.plant_name?.split(' ')[0]}</td>
                    <td className="py-3 px-4 text-slate-300">{inc.machine_id}</td>
                    <td className="py-3 px-4 text-slate-400">{inc.incident_type}</td>
                    <td className="py-3 px-4">
                      <Badge label={inc.severity} size="sm" dot={inc.severity === 'CRITICAL'} />
                    </td>
                    <td className="py-3 px-4">
                      <Badge label={inc.status} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-sans">
                      {inc.assigned_investigator?.split(' ')[0] || 'Unassigned'}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-500 text-[11px]">
                      {inc.created_timestamp.slice(0, 10)}
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
            <span className="text-white font-bold">{totalPages}</span> ({total} Incidents)
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

      {/* Incident Detail Modal with Authentic Chronological Timeline */}
      <Modal
        isOpen={!!selectedIncidentId}
        onClose={() => setSelectedIncidentId(null)}
        title={`Safety Incident Dossier: ${selectedIncidentId}`}
        subtitle={incidentDetail?.incident.title || ''}
        maxWidth="4xl"
      >
        {detailLoading ? (
          <div className="flex items-center justify-center p-12">
            <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin" />
          </div>
        ) : incidentDetail ? (
          <div className="space-y-6 font-mono text-xs">
            {/* Top Stat Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Lifecycle Status</span>
                <div className="mt-1">
                  <Badge label={incidentDetail.incident.status} dot />
                </div>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Severity</span>
                <div className="mt-1">
                  <Badge label={incidentDetail.incident.severity} />
                </div>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Machine Involved</span>
                <p className="text-white font-bold mt-1">
                  {incidentDetail.machine.name} ({incidentDetail.machine.id})
                </p>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Investigator</span>
                <p className="text-cyan-400 font-bold mt-1 truncate">
                  {incidentDetail.incident.assigned_investigator || 'Safety Officer'}
                </p>
              </div>
            </div>

            {/* Status Advancement Workflow Buttons */}
            <div className="p-4 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-slate-400 uppercase text-[10px] font-bold">Investigation Workflow</span>
                <p className="text-slate-300 font-sans text-xs">
                  Advance lifecycle progression under safety compliance protocol.
                </p>
              </div>
              <div className="flex items-center gap-2">
                {incidentDetail.incident.status === 'OPEN' && (
                  <button
                    onClick={() => handleAdvanceStatus('INVESTIGATING')}
                    disabled={advancingStatus}
                    className="px-3 py-1.5 rounded bg-amber-600 hover:bg-amber-500 text-white font-mono text-xs transition-colors"
                  >
                    Start Investigation
                  </button>
                )}
                {incidentDetail.incident.status === 'INVESTIGATING' && (
                  <button
                    onClick={() => handleAdvanceStatus('CONTAINED')}
                    disabled={advancingStatus}
                    className="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white font-mono text-xs transition-colors"
                  >
                    Mark Contained
                  </button>
                )}
                {incidentDetail.incident.status === 'CONTAINED' && (
                  <button
                    onClick={() => handleAdvanceStatus('RESOLVED')}
                    disabled={advancingStatus}
                    className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs transition-colors"
                  >
                    Resolve Incident
                  </button>
                )}
                {incidentDetail.incident.status === 'RESOLVED' && (
                  <button
                    onClick={() => handleAdvanceStatus('CLOSED')}
                    disabled={advancingStatus}
                    className="px-3 py-1.5 rounded bg-green-600 hover:bg-green-500 text-white font-mono text-xs transition-colors"
                  >
                    Close (Verify Requirements)
                  </button>
                )}
                {incidentDetail.incident.status === 'CLOSED' && (
                  <span className="px-3 py-1 rounded bg-slate-800 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                    <CheckCircle className="w-3.5 h-3.5" /> Formal Closure Certified
                  </span>
                )}
              </div>
            </div>

            {/* AUTHENTIC CHRONOLOGICAL TIMELINE (Mandatory Requirement) */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-xs font-semibold uppercase font-mono tracking-wider text-cyan-400 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  Authentic Chronological Lifecycle Timeline
                </h4>
                <span className="text-[10px] text-slate-500 font-mono">
                  Preserved Temporal Ordering (No Fabrication)
                </span>
              </div>

              <div className="relative pl-6 space-y-6 before:content-[''] before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-800">
                {incidentDetail.timeline.map((step, idx) => (
                  <div key={idx} className="relative group">
                    {/* Circle marker */}
                    <div className="absolute -left-[19px] top-1 w-3 h-3 rounded-full bg-slate-900 border-2 border-cyan-400 group-hover:scale-125 transition-transform" />

                    <div className="glass-panel p-3.5 rounded-lg border border-slate-800/80 bg-slate-950/40 hover:border-slate-700 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-xs">{step.stage}</span>
                          {step.event_id && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                              {step.event_id}
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-slate-500">
                          {step.timestamp.slice(0, 19).replace('T', ' ')}
                        </span>
                      </div>

                      <p className="text-xs text-slate-300 font-sans mt-1.5 leading-relaxed">
                        {step.details}
                      </p>

                      {step.actor && (
                        <p className="text-[10px] text-cyan-400 mt-1 font-mono">Actor: {step.actor}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Corrective Actions Section */}
            <div>
              <h4 className="text-xs font-semibold uppercase font-mono tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                <FileText className="w-4 h-4 text-purple-400" /> Required Corrective Actions (
                {incidentDetail.corrective_actions.length})
              </h4>
              <div className="space-y-2">
                {incidentDetail.corrective_actions.map((act) => (
                  <div
                    key={act.id}
                    className="p-3 rounded-lg border border-slate-800 bg-slate-950/50 flex items-center justify-between"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-cyan-400">{act.id}</span>
                        <Badge label={act.status} size="sm" />
                        <Badge
                          label={act.is_verified ? 'VERIFIED' : 'UNVERIFIED'}
                          variant={act.is_verified ? 'success' : 'high'}
                          size="sm"
                        />
                      </div>
                      <p className="text-xs text-white font-sans">{act.title}</p>
                      <p className="text-[11px] text-slate-400">
                        Assigned To: {act.assigned_to} | Due: {act.due_date.slice(0, 10)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};
