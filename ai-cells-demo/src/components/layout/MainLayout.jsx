import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import Header from './Header';
import ChatInterface from '../chat/ChatInterface';
import CellSidebar from '../cells/CellSidebar';
import CellFlow from '../cells/CellFlow';
import { useConfigStore, getThemeClass } from '../../store/configStore';

const MainLayout = () => {
  const { theme } = useConfigStore();

  // Update theme class on body
  useEffect(() => {
    document.body.className = getThemeClass();
  }, [theme]);

  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      <Header />
      
      <main className="flex-1 flex overflow-hidden">
        <CellSidebar />
        
        <div className="flex-1 flex flex-col">
          <div className="flex-1 p-4 overflow-hidden">
            <motion.div
              layout
              className="h-full"
            >
              <ChatInterface />
            </motion.div>
          </div>
        </div>
      </main>

      <footer className="border-t py-4">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>AI Cells Demo</span>
            <span>Built with React + Tailwind</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
