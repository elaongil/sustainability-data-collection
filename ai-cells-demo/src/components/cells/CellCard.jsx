import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Zap, Database, Brain, Cog } from 'lucide-react';
import { useCellStore } from '../../store/cellStore';
import { shouldAnimate } from '../../store/configStore';
import WikipediaCell from './WikipediaCell';
import CDPExtractorCell from './CDPExtractorCell';
import AnnualReportExtractorCell from './AnnualReportExtractorCell';
import EstimatorCell from './EstimatorCell';

const cellIcons = {
  processor: Cpu,
  generator: Zap,
  utility: Cog,
  analyzer: Brain,
  storage: Database,
};

const cellVariants = {
  initial: { 
    opacity: 0,
    scale: 0.9,
  },
  animate: { 
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.2,
    }
  },
  hover: {
    scale: 1.02,
    transition: {
      duration: 0.2,
    }
  },
  tap: {
    scale: 0.98,
  },
};

const CellCard = ({ cell }) => {
  const { toggleCell } = useCellStore();
  const animate = shouldAnimate();
  
  const Icon = cellIcons[cell.type] || Cpu;

  return (
    <motion.div
      variants={cellVariants}
      initial={animate ? "initial" : false}
      animate="animate"
      whileHover="hover"
      whileTap="tap"
      className={`
        cell-card select-none
        ${cell.active ? 'ring-2 ring-primary' : 'hover:border-primary/50'}
      `}
    >
      <div 
        className="flex items-start gap-3"
        onClick={(e) => {
          // Prevent toggling when clicking inside the Wikipedia form or file upload
          if (
            cell.active && 
            (
              (cell.id === 'wikipedia-extractor' && e.target.closest('form')) ||
              (cell.id === 'cdp-extractor' && e.target.closest('form')) ||
              (cell.id === 'annual-report-extractor' && e.target.closest('form')) || 
              (cell.id === 'estimator' && e.target.closest('button'))
            )
          ) {
            e.stopPropagation();
            return;
          }
          toggleCell(cell.id);
        }}
      >
        <div className={`
          p-2 rounded-lg
          ${cell.active ? 'bg-primary text-primary-foreground' : 'bg-muted'}
        `}>
          <Icon className="w-5 h-5" />
        </div>
        
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">{cell.name}</h3>
            <motion.div
              animate={{
                scale: cell.active ? 1 : 0.8,
                opacity: cell.active ? 1 : 0.5,
              }}
              className={`
                w-2 h-2 rounded-full
                ${cell.active ? 'bg-primary' : 'bg-muted-foreground'}
              `}
            />
          </div>
          
          <p className="text-sm text-muted-foreground mt-1">
            {cell.description}
          </p>

          {cell.active && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="mt-2 flex items-center hidden gap-2"
              >
                <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-primary"
                    animate={{
                      width: ['0%', '100%'],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'linear',
                    }}
                  />
                </div>
                <span className="text-xs text-muted-foreground">Active</span>
              </motion.div>

              {cell.id === 'wikipedia-extractor' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2"
                >
                  <WikipediaCell />
                </motion.div>
              )}

            {cell.id === 'cdp-extractor' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2"
                >
                  <CDPExtractorCell />
                </motion.div>
              )}

            {cell.id === 'annual-report-extractor' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2"
                >
                  <AnnualReportExtractorCell />
                </motion.div>
              )} 

              {cell.id === 'estimator' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2"
                >
                  <EstimatorCell />
                </motion.div>
              )} 
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default CellCard;
