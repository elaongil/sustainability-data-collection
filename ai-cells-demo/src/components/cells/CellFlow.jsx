import React, { useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';
import { useCellStore } from '../../store/cellStore';
import { shouldAnimate } from '../../store/configStore';

const nodeTypes = {
  cell: ({ data }) => (
    <div className={`
      p-4 rounded-lg border shadow-sm
      ${data.active ? 'bg-primary text-primary-foreground' : 'bg-card'}
    `}>
      <div className="font-medium">{data.name}</div>
      <div className="text-xs mt-1 opacity-80">{data.type}</div>
    </div>
  ),
};

const CellFlow = () => {
  const { cells, connections, updateCellPosition } = useCellStore();
  const animate = shouldAnimate();

  // Convert cells to ReactFlow nodes
  const initialNodes = cells.map(cell => ({
    id: cell.id,
    type: 'cell',
    position: cell.position,
    data: { ...cell },
  }));

  // Convert connections to ReactFlow edges
  const initialEdges = connections.map(conn => ({
    id: conn.id,
    source: conn.source,
    target: conn.target,
    animated: true,
    style: { stroke: 'hsl(var(--primary))' },
  }));

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update node positions in store when dragged
  const onNodeDragStop = useCallback((event, node) => {
    updateCellPosition(node.id, node.position);
  }, [updateCellPosition]);

  return (
    <motion.div
      initial={animate ? { opacity: 0 } : false}
      animate={animate ? { opacity: 1 } : false}
      transition={{ duration: 0.3 }}
      className="w-full h-full"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeDragStop={onNodeDragStop}
        nodeTypes={nodeTypes}
        fitView
        className="bg-background"
      >
        <Panel position="top-left" className="bg-background/50 p-2 rounded-lg">
          <h3 className="text-sm font-medium">AI Cell Flow</h3>
        </Panel>
        <Background />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            return node.data?.active ? 'hsl(var(--primary))' : 'hsl(var(--muted))';
          }}
        />
      </ReactFlow>
    </motion.div>
  );
};

export default CellFlow;
