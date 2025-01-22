import { create } from 'zustand';

const INITIAL_CELLS = [
  {
    id: 'wikipedia-extractor',
    name: 'Wikipedia Data Extractor',
    description: 'Extracts table data from Wikipedia pages',
    type: 'processor',
    active: false,
    position: { x: 100, y: 550 },
  },
  {
    id: 'entity-recognition',
    name: 'Entity Recognition',
    description: 'Identifies and extracts named entities from text',
    type: 'processor',
    active: false,
    position: { x: 100, y: 100 },
  },
  {
    id: 'semantic-analysis',
    name: 'Semantic Analysis',
    description: 'Analyzes the meaning and context of text',
    type: 'processor',
    active: false,
    position: { x: 100, y: 400 },
  },
  {
    id: 'response-generation',
    name: 'Response Generation',
    description: 'Generates contextually appropriate responses',
    type: 'generator',
    active: false,
    position: { x: 400, y: 250 },
  },
  {
    id: 'cache-management',
    name: 'Cache Management',
    description: 'Manages response caching for improved performance',
    type: 'utility',
    active: false,
    position: { x: 250, y: 400 },
  },
];

const CELL_CONNECTIONS = [
  {
    id: 'wiki-response',
    source: 'wikipedia-extractor',
    target: 'response-generation',
  },
  {
    id: 'semantic-response',
    source: 'semantic-analysis',
    target: 'response-generation',
  },
  {
    id: 'cache-response',
    source: 'cache-management',
    target: 'response-generation',
  },
];

export const useCellStore = create((set) => ({
  cells: INITIAL_CELLS,
  connections: CELL_CONNECTIONS,
  activeCells: [],

  toggleCell: (cellId) =>
    set((state) => {
      const updatedCells = state.cells.map((cell) =>
        cell.id === cellId ? { ...cell, active: !cell.active } : cell
      );
      
      const activeCells = updatedCells.filter((cell) => cell.active);
      
      return {
        cells: updatedCells,
        activeCells,
      };
    }),

  updateCellPosition: (cellId, position) =>
    set((state) => ({
      cells: state.cells.map((cell) =>
        cell.id === cellId ? { ...cell, position } : cell
      ),
    })),

  getActiveConnections: () => {
    const state = useCellStore.getState();
    return state.connections.filter(
      (conn) =>
        state.cells.find((c) => c.id === conn.source)?.active &&
        state.cells.find((c) => c.id === conn.target)?.active
    );
  },

  resetCells: () =>
    set({
      cells: INITIAL_CELLS,
      activeCells: [],
    }),
}));
