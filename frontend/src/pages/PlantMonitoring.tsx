import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Factory,
  MapPin,
  Cpu,
  BellRing,
  AlertTriangle,
  ShieldCheck,
  ArrowRight,
  RefreshCw,
  Layers,
  ChevronRight,
} from 'lucide-react';
import { plantsApi } from '../services/api';
import { Plant } from '../types';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { useFilters } from '../context/FilterContext';

export const PlantMonitoring: React.FC = () => {
  const navigate = useNavigate();
  const { setPlantId } = useFilters();
  const [plants, setPlants] = useState<Plant[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedPlantId, setSelectedPlantId] = useState<string | null>(null);
  const [plantDetail, setPlantDetail] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  const fetchPlants = async () => {
    try {
      setLoading(true);
      const data = await plantsApi.getAll();
      setPlants(data);
    } catch (err) {
      console.error('Error fetching plants:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlants();
  }, []);

  const handleSelectPlant = async (id: string) => {
    try {
      setSelectedPlantId(id);
      setDetailLoading(true);
      const detail = await plantsApi.getById(id);
      setPlantDetail(detail);
    } catch (err) {
      console.error('Error fetching plant detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDrillDownToMachines = (plantId: string) => {
    setPlantId(plantId);
    navigate('/machines');
  };

  const handleDrillDownToAlarms = (plantId: string) => {
    setPlantId(plantId);
    navigate('/alarms');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Plant Site Monitoring</h1>
            <Badge label="4 SITES" variant="info" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Global manufacturing facilities, equipment densities, and containment safety scores.
          </p>
        </div>

        <button
          onClick={fetchPlants}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-mono transition-all self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Sites
        </button>
      </div>

      {/* Plants Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {plants.map((plant) => (
          <div
            key={plant.id}
            onClick={() => handleSelectPlant(plant.id)}
            className="glass-panel rounded-xl p-6 border border-slate-800 hover:border-cyan-500/50 transition-all cursor-pointer group hover:translate-y-[-2px] relative overflow-hidden"
          >
            {/* Top Bar */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                  <Factory className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-cyan-400">{plant.id}</span>
                    <Badge label={plant.operational_status} size="sm" />
                  </div>
                  <h3 className="text-base font-bold text-white mt-1 group-hover:text-cyan-300 transition-colors">
                    {plant.name}
                  </h3>
                  <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-500" />
                    {plant.location}
                  </p>
                </div>
              </div>

              {/* Safety Score Radial Badge */}
              <div className="text-right">
                <span className="text-[10px] font-mono uppercase text-slate-400">Safety Index</span>
                <div className="text-xl font-bold font-mono text-emerald-400">{plant.safety_score}%</div>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-3 gap-3 my-5 pt-4 border-t border-slate-800/80">
              <div className="bg-slate-900/60 rounded-lg p-2.5 border border-slate-800">
                <div className="flex items-center gap-1.5 text-slate-400 text-xs">
                  <Cpu className="w-3.5 h-3.5 text-blue-400" /> Machines
                </div>
                <div className="text-lg font-bold font-mono text-white mt-1">
                  {plant.machines_count || 15}
                </div>
              </div>

              <div className="bg-slate-900/60 rounded-lg p-2.5 border border-slate-800">
                <div className="flex items-center gap-1.5 text-slate-400 text-xs">
                  <BellRing className="w-3.5 h-3.5 text-amber-400" /> Active Alarms
                </div>
                <div className="text-lg font-bold font-mono text-amber-400 mt-1">
                  {plant.active_alarms_count || 0}
                </div>
              </div>

              <div className="bg-slate-900/60 rounded-lg p-2.5 border border-slate-800">
                <div className="flex items-center gap-1.5 text-slate-400 text-xs">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-400" /> Critical Trips
                </div>
                <div className="text-lg font-bold font-mono text-red-400 mt-1">
                  {plant.critical_incidents_count || 0}
                </div>
              </div>
            </div>

            {/* Quick Actions Footer */}
            <div className="flex items-center justify-between text-xs font-mono pt-3 border-t border-slate-800/60">
              <span className="text-slate-400">Total Lines: {plant.total_lines}</span>
              <span className="text-cyan-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                Inspect Site Analytics <ChevronRight className="w-4 h-4" />
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Plant Detail Modal */}
      <Modal
        isOpen={!!selectedPlantId}
        onClose={() => setSelectedPlantId(null)}
        title={plantDetail?.plant?.name || 'Plant Telemetry'}
        subtitle={`Site Location: ${plantDetail?.plant?.location || ''} | Facility ID: ${selectedPlantId}`}
        maxWidth="4xl"
      >
        {detailLoading ? (
          <div className="flex items-center justify-center p-12">
            <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin" />
          </div>
        ) : plantDetail ? (
          <div className="space-y-6">
            {/* Top KPI row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
              <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs">Total Machines</span>
                <p className="text-lg font-bold text-white mt-0.5">{plantDetail.stats.machine_count}</p>
              </div>
              <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs">Total Alarms</span>
                <p className="text-lg font-bold text-cyan-400 mt-0.5">{plantDetail.stats.total_alarms.toLocaleString()}</p>
              </div>
              <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs">Critical Alarms</span>
                <p className="text-lg font-bold text-red-400 mt-0.5">{plantDetail.stats.critical_alarms.toLocaleString()}</p>
              </div>
              <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs">Safety Zones</span>
                <p className="text-lg font-bold text-emerald-400 mt-0.5">{plantDetail.stats.safety_zone_count}</p>
              </div>
            </div>

            {/* Safety Zones Section */}
            <div>
              <h4 className="text-xs font-semibold uppercase font-mono tracking-wider text-slate-400 mb-3">
                Containment Safety Zones
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {plantDetail.safety_zones.map((z: any) => (
                  <div key={z.id} className="p-3 rounded-lg border border-slate-800 bg-slate-950/40">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs text-cyan-400 font-semibold">{z.id}</span>
                      <Badge label={z.hazard_level} size="sm" />
                    </div>
                    <p className="text-xs font-medium text-white mt-1">{z.name}</p>
                    <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                      Type: {z.zone_type} | Max Occupancy: {z.max_occupancy}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Machines List Section */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-semibold uppercase font-mono tracking-wider text-slate-400">
                  Deployed Machinery ({plantDetail.machines.length})
                </h4>
                <button
                  onClick={() => handleDrillDownToMachines(plantDetail.plant.id)}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1"
                >
                  Manage Machinery <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="overflow-x-auto max-h-64 border border-slate-800 rounded-lg">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] sticky top-0">
                    <tr>
                      <th className="p-2.5">ID</th>
                      <th className="p-2.5">Name</th>
                      <th className="p-2.5">Type</th>
                      <th className="p-2.5">State</th>
                      <th className="p-2.5">Criticality</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 bg-slate-950/30">
                    {plantDetail.machines.map((m: any) => (
                      <tr key={m.id} className="hover:bg-slate-900/50">
                        <td className="p-2.5 text-cyan-400 font-semibold">{m.id}</td>
                        <td className="p-2.5 text-slate-200">{m.name}</td>
                        <td className="p-2.5 text-slate-400">{m.type}</td>
                        <td className="p-2.5">
                          <Badge label={m.current_state} size="sm" />
                        </td>
                        <td className="p-2.5">
                          <Badge label={m.criticality} size="sm" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                onClick={() => handleDrillDownToAlarms(plantDetail.plant.id)}
                className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-xs font-mono hover:bg-slate-700 transition-colors"
              >
                View Plant Alarms
              </button>
              <button
                onClick={() => handleDrillDownToMachines(plantDetail.plant.id)}
                className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono font-medium shadow-md transition-colors"
              >
                Inspect All Machines
              </button>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};
