import React from 'react';
import { motion } from 'framer-motion';
import { Trash2, AlertCircle } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { useCellStore } from '../../store/cellStore';
import { shouldAnimate } from '../../store/configStore';
import ChatHistory from './ChatHistory';
import ChatInput from './ChatInput';

const ChatInterface = () => {
  const { clearChat } = useChatStore();
  const { cells } = useCellStore();
  const animate = shouldAnimate();
  
  const activeCellCount = cells.filter(cell => cell.active).length;

  return (
    <motion.div
      initial={animate ? { opacity: 0, scale: 0.95 } : false}
      animate={animate ? { opacity: 1, scale: 1 } : false}
      transition={{ duration: 0.3 }}
      className="flex flex-col h-full bg-background border rounded-lg shadow-sm"
    >
      <div className="border-b p-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold">Chat Interface</h2>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Active Cells: {activeCellCount}
            </span>
            {activeCellCount === 0 && (
              <div className="flex items-center gap-1 text-sm text-yellow-600 dark:text-yellow-400">
                <AlertCircle className="w-4 h-4" />
                <span>No active cells</span>
              </div>
            )}
          </div>
        </div>
        <button
          onClick={clearChat}
          className="p-2 hover:bg-muted rounded-lg transition-colors duration-200"
          title="Clear chat history"
        >
          <Trash2 className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>

      <div className="flex-1 min-h-0 relative">
        <ChatHistory />
      </div>
      <div className="flex-shrink-0">
        <ChatInput />
      </div>
    </motion.div>
  );
};

export default ChatInterface;
