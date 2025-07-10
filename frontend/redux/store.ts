import { configureStore } from '@reduxjs/toolkit';
import reparseReducer from './reparseSlice';

export const store = configureStore({
  reducer: {
    reparse: reparseReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;