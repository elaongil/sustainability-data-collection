import React, { useEffect } from 'react';
import { ReactFlowProvider } from 'reactflow';
import MainLayout from './components/layout/MainLayout';
import { v4 as uuidv4 } from 'uuid';
import { getSessionId } from './components/sessionUtils';

function App() {

  useEffect(() => {
    getSessionId();
  },[]);

  return (
    <ReactFlowProvider>
      <MainLayout />
    </ReactFlowProvider>
  );
}

export default App;
