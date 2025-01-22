import React from 'react';
import { ReactFlowProvider } from 'reactflow';
import MainLayout from './components/layout/MainLayout';

function App() {
  return (
    <ReactFlowProvider>
      <MainLayout />
    </ReactFlowProvider>
  );
}

export default App;
