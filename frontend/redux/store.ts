import { configureStore } from '@reduxjs/toolkit';

import reparseReducer from './reparseSlice';
import channelReducer from './channelslice';
import feedsReducer from './feedSlice';

export const store = configureStore({
  reducer: {
    reparse: reparseReducer,
    channel: channelReducer,
    feeds: feedsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;