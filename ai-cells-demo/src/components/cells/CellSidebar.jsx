import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Power, RefreshCw } from 'lucide-react';
import { useCellStore } from '../../store/cellStore';
import { shouldAnimate } from '../../store/configStore';
import CellCard from './CellCard';

const CellSidebar = () => {
  const { cells, resetCells } = useCellStore();
  const animate = shouldAnimate();
  
  const activeCells = cells.filter(cell => cell.active);
  const inactiveCells = cells.filter(cell => !cell.active);

  return (
    <motion.div
      initial={animate ? { opacity: 0, x: -20 } : false}
      animate={animate ? { opacity: 1, x: 0 } : false}
      transition={{ duration: 0.3 }}
      className="w-80 border-r bg-card flex flex-col h-full"
    >
      <div className="border-b p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">AI Cells</h2>
          <button
            onClick={resetCells}
            className="p-2 hover:bg-muted rounded-lg transition-colors duration-200"
            title="Reset all cells"
          >
            <RefreshCw className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>

        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Power className="w-4 h-4" />
            <span>Active Cells: {activeCells.length}</span>
          </div>
          <span>{Math.round((activeCells.length / cells.length) * 100)}% Active</span>
        </div>

        {activeCells.length > 0 && (
          <div className="mt-2 h-1 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${(activeCells.length / cells.length) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <AnimatePresence mode="popLayout">
          {activeCells.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="mb-4">
                <h3 className="text-sm font-medium mb-3">Active Cells</h3>
                <div className="space-y-3">
                  {activeCells.map(cell => (
                    <CellCard key={cell.id} cell={cell} />
                  ))}
                </div>
              </div>
              <div className="border-t my-4" />
            </motion.div>
          )}

          <div>
            <h3 className="text-sm font-medium mb-3">
              {activeCells.length > 0 ? 'Available Cells' : 'All Cells'}
            </h3>
            <div className="space-y-3">
              {inactiveCells.map(cell => (
                <CellCard key={cell.id} cell={cell} />
              ))}
            </div>
          </div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default CellSidebar;
