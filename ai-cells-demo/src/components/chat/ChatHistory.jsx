import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '../../store/chatStore';
import { shouldAnimate } from '../../store/configStore';
import ChatMessage from './ChatMessage';

const ChatHistory = () => {
  const { messages, isProcessing, processingSteps } = useChatStore();
  const messagesEndRef = useRef(null);
  const animate = shouldAnimate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isProcessing]);

  return (
    <div className="absolute inset-0 overflow-y-auto p-4">
      <div className="max-w-3xl mx-auto space-y-4">
        {messages.length === 0 ? (
          <motion.div
            initial={animate ? { opacity: 0, y: 20 } : false}
            animate={animate ? { opacity: 1, y: 0 } : false}
            transition={{ duration: 0.3 }}
            className="text-center text-muted-foreground p-8"
          >
            <p>No messages yet. Start a conversation!</p>
            <p className="text-sm mt-2">
              Try activating some AI cells in the sidebar to enhance the AI's capabilities.
            </p>
          </motion.div>
        ) : (
          <AnimatePresence mode="popLayout">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isProcessing={
                  isProcessing &&
                  message.type === 'ai' &&
                  message.id === Math.max(...messages.map((m) => m.id))
                }
              />
            ))}
          </AnimatePresence>
        )}

        {isProcessing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="bg-muted/50 rounded-lg p-4 space-y-2"
          >
            <div className="text-sm font-medium">Processing Steps:</div>
            <div className="space-y-1">
              {processingSteps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-sm text-muted-foreground flex items-center gap-2"
                >
                  <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                  <span>{step.split('-').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatHistory;
