import React, { createContext, useContext, useState, ReactNode } from 'react';

interface FilterState {
  plantId: string;
  machineId: string;
  severity: string;
  dateRange: string;
  searchQuery: string;
}

interface FilterContextType {
  filters: FilterState;
  setPlantId: (id: string) => void;
  setMachineId: (id: string) => void;
  setSeverity: (severity: string) => void;
  setDateRange: (range: string) => void;
  setSearchQuery: (query: string) => void;
  resetFilters: () => void;
}

const defaultFilters: FilterState = {
  plantId: '',
  machineId: '',
  severity: '',
  dateRange: '30d',
  searchQuery: '',
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [filters, setFilters] = useState<FilterState>(defaultFilters);

  const setPlantId = (plantId: string) => setFilters(prev => ({ ...prev, plantId, machineId: '' }));
  const setMachineId = (machineId: string) => setFilters(prev => ({ ...prev, machineId }));
  const setSeverity = (severity: string) => setFilters(prev => ({ ...prev, severity }));
  const setDateRange = (dateRange: string) => setFilters(prev => ({ ...prev, dateRange }));
  const setSearchQuery = (searchQuery: string) => setFilters(prev => ({ ...prev, searchQuery }));
  const resetFilters = () => setFilters(defaultFilters);

  return (
    <FilterContext.Provider
      value={{
        filters,
        setPlantId,
        setMachineId,
        setSeverity,
        setDateRange,
        setSearchQuery,
        resetFilters,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};
