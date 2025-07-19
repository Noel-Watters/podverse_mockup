import { configureStore } from '@reduxjs/toolkit';

import reparseReducer from './reparseSlice';
import batchChannelReducer from './batchChannelSlice';
import feedsReducer from './feedSlice';

export const store = configureStore({
  reducer: {
    reparse: reparseReducer,
    batchChannel: batchChannelReducer,
    feeds: feedsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;