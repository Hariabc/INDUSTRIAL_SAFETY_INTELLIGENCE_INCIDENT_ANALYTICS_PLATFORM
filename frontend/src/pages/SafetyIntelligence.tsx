import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  Play,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  FileText,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { toast } from 'react-toastify';
import { anomaliesApi, analyticsApi } from '../services/api';
import { SafetyAnomaly, ModelPerformance } from '../types';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { useFilters } from '../context/FilterContext';

export const SafetyIntelligence: React.FC = () => {
  const { filters } = useFilters();
  const [anomalies, setAnomalies] = useState<SafetyAnomaly[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [runningPipeline, setRunningPipeline] = useState<boolean>(false);

  const [typeFilter, setTypeFilter] = useState<string>('');
  const [sevFilter, setSevFilter] = useState<string>('');
  const [performance, setPerformance] = useState<ModelPerformance | null>(null);

  const [selectedAnomaly, setSelectedAnomaly] = useState<SafetyAnomaly | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [anomRes, evalRes] = await Promise.all([
        anomaliesApi.getAll({
          anomaly_type: typeFilter || undefined,
          severity: sevFilter || filters.severity || undefined,
          plant_id: filters.plantId || undefined,
          machine_id: filters.machineId || undefined,
          search: filters.searchQuery || undefined,
          page,
          page_size: 15,
        }),
        analyticsApi.getModelEvaluation(),
      ]);

      setAnomalies(anomRes.items);
      setTotal(anomRes.total);
      setTotalPages(anomRes.total_pages);
      setPerformance(evalRes.model_performance);
    } catch (err) {
      console.error('Error fetching safety intelligence:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters.plantId, filters.machineId, filters.severity, filters.searchQuery, typeFilter, sevFilter, page]);

  const handleRunDetection = async () => {
    try {
      setRunningPipeline(true);
      const res = await anomaliesApi.runDetection();
      toast.success(
        `Detection Complete: Identified ${res.detections_count} anomalies. F1 Score: ${(
          res.evaluation.model_performance.f1_score * 100
        ).toFixed(1)}%`
      );
      await fetchData();
    } catch (err) {
      toast.error('Detection pipeline execution failed.');
      console.error(err);
    } finally {
      setRunningPipeline(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Safety Intelligence Engine</h1>
            <Badge label="8 RULES ACTIVE" variant="info" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Explainable anomaly detection across repeated unsafe states, flood events, nuisance alarms, and protocol violations.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start">
          <button
            onClick={handleRunDetection}
            disabled={runningPipeline}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-mono font-bold shadow-lg glow-cyan transition-all disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${runningPipeline ? 'animate-spin' : ''}`} />
            {runningPipeline ? 'Executing Rules...' : 'Run Detection Pipeline'}
          </button>

          <button
            onClick={fetchData}
            className="p-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Model Benchmark Performance Bar */}
      {performance && (
        <div className="glass-panel rounded-xl p-5 border border-cyan-500/30 bg-gradient-to-br from-industrial-900 to-slate-900/60 shadow-xl">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider font-mono text-cyan-400">
                Ground-Truth Detection Performance (Benchmark Evaluation)
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-400">
              Ground Truth Population: <strong className="text-white">{performance.ground_truth_total}</strong> Anomalies
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3 font-mono">
            <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">Precision</span>
              <p className="text-lg font-bold text-emerald-400 mt-0.5">
                {(performance.precision * 100).toFixed(1)}%
              </p>
            </div>
            <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">Recall</span>
              <p className="text-lg font-bold text-emerald-400 mt-0.5">
                {(performance.recall * 100).toFixed(1)}%
              </p>
            </div>
            <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">F1 Score</span>
              <p className="text-lg font-bold text-cyan-400 mt-0.5">
                {(performance.f1_score * 100).toFixed(1)}%
              </p>
            </div>
            <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">Detection Coverage</span>
              <p className="text-lg font-bold text-cyan-400 mt-0.5">
                {(performance.detection_coverage * 100).toFixed(1)}%
              </p>
            </div>
            <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">True Positives</span>
              <p className="text-lg font-bold text-white mt-0.5">{performance.true_positives}</p>
            </div>
            <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">False Negatives</span>
              <p className="text-lg font-bold text-slate-400 mt-0.5">{performance.false_negatives}</p>
            </div>
          </div>
        </div>
      )}

      {/* Local Filter Bar */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
        >
          <option value="">All Anomaly Types (8)</option>
          <option value="REPEATED_UNSAFE_CONDITION">Repeated Unsafe Condition</option>
          <option value="DELAYED_ACKNOWLEDGEMENT">Delayed Acknowledgement</option>
          <option value="ALARM_FLOOD">Alarm Flood</option>
          <option value="NUISANCE_ALARM">Nuisance Alarm</option>
          <option value="INTERLOCK_VIOLATION">Interlock Violation</option>
          <option value="MISSING_INCIDENT_CONTEXT">Missing Incident Context</option>
          <option value="DUPLICATE_ALARM_REPLAY">Duplicate Alarm Replay</option>
          <option value="INCOMPLETE_CORRECTIVE_ACTION">Incomplete Corrective Action</option>
        </select>

        <select
          value={sevFilter}
          onChange={(e) => {
            setSevFilter(e.target.value);
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
      </div>

      {/* Anomalies Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Anomaly ID</th>
                <th className="py-3 px-4">Anomaly Type</th>
                <th className="py-3 px-4">Machine / Plant</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Explainable Rationale</th>
                <th className="py-3 px-4">Recommended Action</th>
                <th className="py-3 px-4 text-right">Detection Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-industrial-950/40">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mx-auto mb-2" />
                    Scanning safety events...
                  </td>
                </tr>
              ) : anomalies.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No safety anomalies detected under the current filters.
                  </td>
                </tr>
              ) : (
                anomalies.map((a) => (
                  <tr
                    key={a.id}
                    onClick={() => setSelectedAnomaly(a)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-bold text-cyan-400 group-hover:underline">
                      {a.id}
                    </td>
                    <td className="py-3 px-4 text-slate-200">
                      <span className="font-semibold">{a.anomaly_type.replace(/_/g, ' ')}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      {a.machine_id ? `${a.machine_id} (${a.plant_id || ''})` : a.plant_id || 'ENTERPRISE'}
                    </td>
                    <td className="py-3 px-4">
                      <Badge label={a.severity} size="sm" dot={a.severity === 'CRITICAL'} />
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-sans truncate max-w-xs">
                      {a.explanation}
                    </td>
                    <td className="py-3 px-4 text-cyan-300 font-sans truncate max-w-xs">
                      {a.recommended_action}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-500 text-[11px]">
                      {a.detection_timestamp.slice(0, 19).replace('T', ' ')}
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
            <span className="text-white font-bold">{totalPages}</span> ({total} Findings)
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

      {/* Anomaly Detail Modal */}
      <Modal
        isOpen={!!selectedAnomaly}
        onClose={() => setSelectedAnomaly(null)}
        title={`Safety Anomaly: ${selectedAnomaly?.id || ''}`}
        subtitle={`Classification: ${selectedAnomaly?.anomaly_type || ''}`}
        maxWidth="2xl"
      >
        {selectedAnomaly && (
          <div className="space-y-5 font-mono text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Severity Tier</span>
                <div className="mt-1">
                  <Badge label={selectedAnomaly.severity} dot />
                </div>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Affected Asset</span>
                <p className="text-white font-bold mt-1">
                  {selectedAnomaly.machine_id || 'Plant-Wide Protocol'} ({selectedAnomaly.plant_id || ''})
                </p>
              </div>
            </div>

            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-2">
              <span className="text-slate-400 font-bold uppercase text-[10px]">Explainable Root Cause Rationale</span>
              <p className="text-slate-200 font-sans leading-relaxed text-sm">{selectedAnomaly.explanation}</p>
            </div>

            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-2">
              <span className="text-slate-400 font-bold uppercase text-[10px]">Recommended Operational Action</span>
              <p className="text-cyan-300 font-sans leading-relaxed text-sm">{selectedAnomaly.recommended_action}</p>
            </div>

            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-2">
              <span className="text-slate-400 font-bold uppercase text-[10px]">Correlated Event Evidence</span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {selectedAnomaly.related_event_ids?.map((evId, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 text-[11px]"
                  >
                    {evId}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
