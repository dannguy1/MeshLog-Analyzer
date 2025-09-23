import { configureStore } from '@reduxjs/toolkit'
import projectsReducer from './features/projects/projectsSlice'
import analysisReducer from './features/analysis/analysisSlice'
import visualizationReducer from './features/visualization/visualizationSlice'
import alertsReducer from './features/alerts/alertsSlice'

export const store = configureStore({
  reducer: {
    projects: projectsReducer,
    analysis: analysisReducer,
    visualization: visualizationReducer,
    alerts: alertsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
