import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { shouldAnimate } from '../../store/configStore';

const ChatInput = () => {
  const [message, setMessage] = useState('');
  const { addMessage, isProcessing } = useChatStore();
  const animate = shouldAnimate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isProcessing) return;

    const trimmedMessage = message.trim();
    setMessage('');
    await addMessage(trimmedMessage);
  };

  return (
    <motion.div
      initial={animate ? { opacity: 0, y: 20 } : false}
      animate={animate ? { opacity: 1, y: 0 } : false}
      transition={{ duration: 0.3 }}
      className="border-t bg-background p-4"
    >
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={isProcessing}
          className="chat-input flex-1 focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button
          type="submit"
          disabled={!message.trim() || isProcessing}
          className={`px-4 py-2 rounded-lg bg-primary text-primary-foreground flex items-center gap-2
            ${!message.trim() || isProcessing ? 'opacity-50 cursor-not-allowed' : 'hover:bg-primary/90'}
            transition-colors duration-200
          `}
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Processing</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Send</span>
            </>
          )}
        </button>
      </form>
      {isProcessing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="mt-2 text-sm text-muted-foreground"
        >
          AI is processing your message...
        </motion.div>
      )}
    </motion.div>
  );
};

export default ChatInput;
