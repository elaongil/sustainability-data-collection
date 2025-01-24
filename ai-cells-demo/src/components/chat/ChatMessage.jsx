import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';


const messageVariants = {
  initial: { 
    opacity: 0,
    y: 20,
  },
  animate: { 
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
    }
  },
  exit: { 
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.2,
    }
  }
};

const ChatMessage = ({ message, isProcessing }) => {
  const { content, type, timestamp } = message;
  const isUser = type === 'user';

  return (
    <motion.div
      className={`chat-message ${type}`}
      variants={messageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      layout
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
          {isUser ? (
            <MessageSquare className="w-4 h-4 text-primary-foreground" />
          ) : (
            <Bot className="w-4 h-4 text-primary-foreground" />
          )}
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium">
              {isUser ? 'You' : 'AI Assistant'}
            </span>
            <span className="text-xs text-muted-foreground">
              {new Date(timestamp).toLocaleTimeString()}
            </span>
          </div>
          <div className="prose prose-sm max-w-none">
            {isProcessing ? (
              <div className="flex items-center gap-2">
                <div className="animate-pulse">Processing</div>
                <div className="flex gap-1">
                  <span className="animate-bounce delay-0">.</span>
                  <span className="animate-bounce delay-100">.</span>
                  <span className="animate-bounce delay-200">.</span>
                </div>
              </div>
            ) : (
              <ReactMarkdown
                className="whitespace-pre-wra"
                remarkPlugins={[
                  remarkGfm,
                  () => (tree) => {
                    //console.log('Markdown AST:', JSON.stringify(tree, null, 2));
                    return tree;
                  }
                ]}
                rehypePlugins={[
                  rehypeRaw,
                  () => (tree) => {
                    //console.log('HTML AST:', JSON.stringify(tree, null, 2));
                    return tree;
                  }
                ]}
                components={{
                  table: ({ children, node, ...props }) => {
                    console.log('Table props:', props);
                    console.log('Table node:', node);
                    return (
                    <div className="my-4 border rounded-lg overflow-hidden">
                      <div className="overflow-x-auto h-80">
                        <table className="w-full">
                          {children}
                        </table>
                      </div>
                    </div>
                    );
                  },
                  thead: ({ children }) => (
                    <thead>
                      {children}
                    </thead>
                  ),
                  tbody: ({ children }) => (
                    <tbody>
                      {children}
                    </tbody>
                  ),
                  tr: ({ children }) => (
                    <tr className="border-b last:border-0">
                      {children}
                    </tr>
                  ),
                  th: ({ children }) => (
                    <th className="p-2 text-left font-medium bg-muted/50 min-w-[100px]">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="p-2">
                      {children}
                    </td>
                  ),
                  pre: ({ children }) => (
                    <pre className="whitespace-pre-wrap font-mono bg-muted/50 p-2 rounded-md overflow-x-auto">{children}</pre>
                  ),
                  code: ({ children }) => (
                    <code className="font-mono bg-muted/50 px-1 py-0.5 rounded">{children}</code>
                  ),
                  p: ({ children }) => (
                    <p className="mb-2 last:mb-0">{children}</p>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-lg font-semibold mt-4 mb-2 text-red-500">{children}</h3>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-red-500">{children}</strong>
                  ),
                }}
              >
                {content}
              </ReactMarkdown>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;
