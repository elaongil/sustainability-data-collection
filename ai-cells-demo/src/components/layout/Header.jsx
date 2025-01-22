import React from 'react';
import { motion } from 'framer-motion';
import { Moon, Sun, Settings, LayoutGrid, Activity } from 'lucide-react';
import { useConfigStore } from '../../store/configStore';
import { shouldAnimate } from '../../store/configStore';

const Header = () => {
  const {
    theme,
    toggleTheme,
    animationsEnabled,
    toggleAnimations,
    processingIndicatorsEnabled,
    toggleProcessingIndicators,
  } = useConfigStore();
  
  const animate = shouldAnimate();

  return (
    <motion.header
      initial={animate ? { opacity: 0, y: -20 } : false}
      animate={animate ? { opacity: 1, y: 0 } : false}
      transition={{ duration: 0.3 }}
      className="border-b bg-background"
    >
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-6 h-6 text-primary" />
          <h1 className="text-xl font-semibold">AI Cells Demo</h1>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <LayoutGrid className="w-4 h-4" />
            <span>AI Cell Visualization</span>
          </div>

          <div className="h-6 w-px bg-border" />

          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 hover:bg-muted rounded-lg transition-colors duration-200"
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4" />
              ) : (
                <Moon className="w-4 h-4" />
              )}
            </button>

            <div className="flex items-center">
              <button
                onClick={toggleAnimations}
                className={`
                  p-2 hover:bg-muted rounded-lg transition-colors duration-200
                  ${animationsEnabled ? 'text-primary' : 'text-muted-foreground'}
                `}
                title={animationsEnabled ? 'Disable animations' : 'Enable animations'}
              >
                <motion.div
                  animate={{ rotate: animationsEnabled ? 360 : 0 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <Settings className="w-4 h-4" />
                </motion.div>
              </button>
            </div>

            <button
              onClick={toggleProcessingIndicators}
              className={`
                p-2 hover:bg-muted rounded-lg transition-colors duration-200
                ${processingIndicatorsEnabled ? 'text-primary' : 'text-muted-foreground'}
              `}
              title={processingIndicatorsEnabled ? 'Hide processing indicators' : 'Show processing indicators'}
            >
              <Activity className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
