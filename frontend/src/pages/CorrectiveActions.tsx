import React, { useEffect, useState } from 'react';
import {
  CheckSquare,
  ShieldCheck,
  AlertCircle,
  Plus,
  RefreshCw,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  UserCheck,
  Lock,
} from 'lucide-react';
import { toast } from 'react-toastify';
import { correctiveActionsApi } from '../services/api';
import { CorrectiveAction } from '../types';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { useFilters } from '../context/FilterContext';

export const CorrectiveActions: React.FC = () => {
  const { filters } = useFilters();
  const [actions, setActions] = useState<CorrectiveAction[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [verifiedFilter, setVerifiedFilter] = useState<string>('');

  // Modals
  const [selectedAction, setSelectedAction] = useState<CorrectiveAction | null>(null);
  const [isVerifyModalOpen, setIsVerifyModalOpen] = useState<boolean>(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false);

  // Forms
  const [verifierName, setVerifierName] = useState<string>('Dr. Aris Thorne (Chief Safety Officer)');
  const [verificationNotes, setVerificationNotes] = useState<string>('Comprehensive physical verification completed. All mechanical clearances conform to safety tolerances.');
  const [newStatus, setNewStatus] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Create form state
  const [newIncidentId, setNewIncidentId] = useState<string>('INC-2026-000001');
  const [newTitle, setNewTitle] = useState<string>('Inspect servo interlock switch and recalibrate deadband');
  const [newAssigned, setNewAssigned] = useState<string>('Marcus Vance');
  const [newPriority, setNewPriority] = useState<string>('HIGH');

  const fetchActions = async () => {
    try {
      setLoading(true);
      const data = await correctiveActionsApi.getAll({
        status: statusFilter || undefined,
        priority: priorityFilter || filters.severity || undefined,
        is_verified: verifiedFilter === '' ? undefined : verifiedFilter === 'true',
        search: filters.searchQuery || undefined,
        page,
        page_size: 15,
      });

      setActions(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching corrective actions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
  }, [filters.severity, filters.searchQuery, statusFilter, priorityFilter, verifiedFilter, page]);

  const handleOpenAction = (act: CorrectiveAction) => {
    setSelectedAction(act);
    setNewStatus(act.status);
    setIsVerifyModalOpen(true);
  };

  const handleVerify = async () => {
    if (!selectedAction) return;
    try {
      setSubmitting(true);
      await correctiveActionsApi.verify(selectedAction.id, {
        verified_by: verifierName,
        verification_notes: verificationNotes,
      });
      toast.success(`Action ${selectedAction.id} verified and signed off successfully.`);
      setIsVerifyModalOpen(false);
      await fetchActions();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Verification submission failed.';
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusUpdate = async () => {
    if (!selectedAction) return;

    // Frontend pre-check for Business Rule: cannot close without verification
    if (newStatus === 'CLOSED' && selectedAction.verification_required && !selectedAction.is_verified) {
      toast.error(
        'Safety Governance Rule: Cannot close corrective action without mandatory safety verification sign-off!'
      );
      return;
    }

    try {
      setSubmitting(true);
      await correctiveActionsApi.updateStatus(selectedAction.id, {
        status: newStatus,
        actor: verifierName,
      });
      toast.success(`Action status updated to ${newStatus}`);
      setIsVerifyModalOpen(false);
      await fetchActions();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to update action status.';
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateAction = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await correctiveActionsApi.create({
        incident_id: newIncidentId,
        title: newTitle,
        assigned_to: newAssigned,
        priority: newPriority,
        due_date: new Date(Date.now() + 7 * 86400000).toISOString(),
      });
      toast.success('New corrective action initiated successfully.');
      setIsCreateModalOpen(false);
      await fetchActions();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to create corrective action.';
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Corrective Actions & Safety Sign-off</h1>
            <Badge label={`${total} ACTIONS`} variant="info" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Mandatory remediation tracking, safety officer verifications, and closure policy enforcement.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start">
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono font-medium shadow-md transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            Create Work Order
          </button>

          <button
            onClick={fetchActions}
            className="p-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Local Filter Bar */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
        >
          <option value="">All Statuses</option>
          <option value="PENDING">PENDING</option>
          <option value="IN_PROGRESS">IN PROGRESS</option>
          <option value="COMPLETED">COMPLETED</option>
          <option value="CLOSED">CLOSED</option>
        </select>

        <select
          value={verifiedFilter}
          onChange={(e) => {
            setVerifiedFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
        >
          <option value="">All Verifications</option>
          <option value="true">VERIFIED</option>
          <option value="false">UNVERIFIED</option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) => {
            setPriorityFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none font-mono"
        >
          <option value="">All Priorities</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>
      </div>

      {/* Actions Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Action ID</th>
                <th className="py-3 px-4">Incident ID</th>
                <th className="py-3 px-4">Remediation Task</th>
                <th className="py-3 px-4">Assigned Engineer</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Verification</th>
                <th className="py-3 px-4 text-right">Due Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-industrial-950/40">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mx-auto mb-2" />
                    Loading action items...
                  </td>
                </tr>
              ) : actions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    No corrective actions match the selected filters.
                  </td>
                </tr>
              ) : (
                actions.map((act) => (
                  <tr
                    key={act.id}
                    onClick={() => handleOpenAction(act)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-bold text-cyan-400 group-hover:underline">
                      {act.id}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{act.incident_id}</td>
                    <td className="py-3 px-4 text-slate-200 font-sans font-medium truncate max-w-sm">
                      {act.title}
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-sans">{act.assigned_to}</td>
                    <td className="py-3 px-4">
                      <Badge label={act.priority} size="sm" dot={act.priority === 'CRITICAL'} />
                    </td>
                    <td className="py-3 px-4">
                      <Badge label={act.status} size="sm" />
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        label={act.is_verified ? 'VERIFIED' : 'PENDING SIGN-OFF'}
                        variant={act.is_verified ? 'success' : 'high'}
                        size="sm"
                      />
                    </td>
                    <td className="py-3 px-4 text-right text-slate-500 text-[11px]">
                      {act.due_date.slice(0, 10)}
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
            <span className="text-white font-bold">{totalPages}</span> ({total} Actions)
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

      {/* Action Detail & Verification Modal */}
      <Modal
        isOpen={isVerifyModalOpen}
        onClose={() => setIsVerifyModalOpen(false)}
        title={`Action Item: ${selectedAction?.id || ''}`}
        subtitle={`Parent Incident: ${selectedAction?.incident_id || ''}`}
        maxWidth="2xl"
      >
        {selectedAction && (
          <div className="space-y-5 font-mono text-xs">
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Action Procedure</span>
              <p className="text-white font-sans text-sm font-medium">{selectedAction.title}</p>
              <p className="text-slate-400 font-sans text-xs">{selectedAction.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Assigned Engineer</span>
                <p className="text-white font-bold mt-1 font-sans">{selectedAction.assigned_to}</p>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400">Verification Status</span>
                <div className="mt-1">
                  <Badge
                    label={selectedAction.is_verified ? 'VERIFIED' : 'UNVERIFIED'}
                    variant={selectedAction.is_verified ? 'success' : 'high'}
                    dot
                  />
                </div>
              </div>
            </div>

            {/* Lifecycle Status Modification */}
            <div className="p-4 bg-slate-950/80 rounded-lg border border-slate-800 space-y-3">
              <span className="text-slate-400 uppercase text-[10px] font-bold">Lifecycle State Management</span>
              <div className="flex items-center gap-3">
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none flex-1 font-mono"
                >
                  <option value="PENDING">PENDING</option>
                  <option value="IN_PROGRESS">IN PROGRESS</option>
                  <option value="COMPLETED">COMPLETED</option>
                  <option value="CLOSED">CLOSED (Requires Verification)</option>
                </select>

                <button
                  onClick={handleStatusUpdate}
                  disabled={submitting || newStatus === selectedAction.status}
                  className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs transition-colors disabled:opacity-40"
                >
                  Update State
                </button>
              </div>

              {newStatus === 'CLOSED' && !selectedAction.is_verified && (
                <div className="flex items-center gap-2 text-red-400 text-[11px] font-sans">
                  <Lock className="w-3.5 h-3.5" />
                  <strong>Enforced Rule:</strong> Action cannot be marked CLOSED until safety verification has been recorded below.
                </div>
              )}
            </div>

            {/* Verification Sign-off Form */}
            <div className="p-4 bg-slate-950/80 rounded-lg border border-slate-800 space-y-3">
              <span className="text-slate-400 uppercase text-[10px] font-bold flex items-center gap-1.5">
                <UserCheck className="w-3.5 h-3.5 text-emerald-400" /> Safety Officer Verification Sign-off
              </span>

              {selectedAction.is_verified ? (
                <div className="p-3 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 space-y-1">
                  <p className="font-bold flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4" /> Safety Verification Certified
                  </p>
                  <p className="text-[11px]">Verified by: {selectedAction.verified_by}</p>
                  <p className="text-[11px]">Notes: {selectedAction.verification_notes}</p>
                  <p className="text-[10px] text-emerald-500/80">
                    Timestamp: {selectedAction.verified_at?.slice(0, 19).replace('T', ' ')}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Verifying Safety Officer</label>
                    <input
                      type="text"
                      value={verifierName}
                      onChange={(e) => setVerifierName(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Verification Evaluation Remarks</label>
                    <textarea
                      rows={2}
                      value={verificationNotes}
                      onChange={(e) => setVerificationNotes(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none font-sans"
                    />
                  </div>
                  <button
                    onClick={handleVerify}
                    disabled={submitting}
                    className="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-mono font-bold text-xs transition-colors shadow-md"
                  >
                    Certify Safety Sign-off
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Create Action Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Initiate Corrective Work Order"
        subtitle="Mandatory corrective remediation linked to safety incident"
        maxWidth="lg"
      >
        <form onSubmit={handleCreateAction} className="space-y-4 text-xs font-mono">
          <div>
            <label className="text-slate-400 block mb-1">Incident Reference ID</label>
            <input
              type="text"
              required
              value={newIncidentId}
              onChange={(e) => setNewIncidentId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="text-slate-400 block mb-1">Procedure Description / Title</label>
            <input
              type="text"
              required
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none font-sans"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-slate-400 block mb-1">Assigned Engineer</label>
              <input
                type="text"
                required
                value={newAssigned}
                onChange={(e) => setNewAssigned(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none font-sans"
              />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Priority Tier</label>
              <select
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none"
              >
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
              </select>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono font-bold text-xs transition-colors"
            >
              Submit Corrective Action Order
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
