import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useConfigStore = create(
  persist(
    (set) => ({
      theme: 'light',
      animationsEnabled: true,
      processingIndicatorsEnabled: true,
      debugMode: false,

      toggleTheme: () =>
        set((state) => ({
          theme: state.theme === 'light' ? 'dark' : 'light',
        })),

      toggleAnimations: () =>
        set((state) => ({
          animationsEnabled: !state.animationsEnabled,
        })),

      toggleProcessingIndicators: () =>
        set((state) => ({
          processingIndicatorsEnabled: !state.processingIndicatorsEnabled,
        })),

      toggleDebugMode: () =>
        set((state) => ({
          debugMode: !state.debugMode,
        })),

      updateConfig: (updates) =>
        set((state) => ({
          ...state,
          ...updates,
        })),

      resetConfig: () =>
        set({
          theme: 'light',
          animationsEnabled: true,
          processingIndicatorsEnabled: true,
          debugMode: false,
        }),
    }),
    {
      name: 'ai-cells-config',
    }
  )
);

// Theme utility functions
export const getThemeClass = () => {
  const { theme } = useConfigStore.getState();
  return theme === 'dark' ? 'dark' : '';
};

export const shouldAnimate = () => {
  const { animationsEnabled } = useConfigStore.getState();
  return animationsEnabled;
};

export const shouldShowProcessing = () => {
  const { processingIndicatorsEnabled } = useConfigStore.getState();
  return processingIndicatorsEnabled;
};

export const isDebugMode = () => {
  const { debugMode } = useConfigStore.getState();
  return debugMode;
};
