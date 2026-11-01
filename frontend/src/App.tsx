import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { FilterProvider } from './context/FilterContext';
import { Layout } from './components/layout/Layout';
import { OverviewDashboard } from './pages/OverviewDashboard';
import { PlantMonitoring } from './pages/PlantMonitoring';
import { MachineMonitoring } from './pages/MachineMonitoring';
import { AlarmAnalytics } from './pages/AlarmAnalytics';
import { SafetyIntelligence } from './pages/SafetyIntelligence';
import { IncidentManagement } from './pages/IncidentManagement';
import { CorrectiveActions } from './pages/CorrectiveActions';
import { DataQuality } from './pages/DataQuality';
import { SystemSettings } from './pages/SystemSettings';

export const App: React.FC = () => {
  return (
    <FilterProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<OverviewDashboard />} />
            <Route path="plants" element={<PlantMonitoring />} />
            <Route path="machines" element={<MachineMonitoring />} />
            <Route path="alarms" element={<AlarmAnalytics />} />
            <Route path="safety" element={<SafetyIntelligence />} />
            <Route path="incidents" element={<IncidentManagement />} />
            <Route path="actions" element={<CorrectiveActions />} />
            <Route path="data-quality" element={<DataQuality />} />
            <Route path="settings" element={<SystemSettings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </FilterProvider>
  );
};

export default App;
