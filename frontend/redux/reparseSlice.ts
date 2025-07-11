// In redux/reparseSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { FeedLog } from '@/types/feed';

// Map of backend status codes to frontend status strings
const statusMap: Record<number, 'live' | 'flagged' | 'error'> = {
  1: 'live',
  2: 'flagged',
  3: 'error',
};

// Types for per-feed async state
interface FeedAsyncState {
  status: 'pending' | 'idle' | 'error' | 'live' | 'flagged';
  loading: boolean;
  reparsing?: boolean; 
  error: string | null;
  success: boolean;
}

interface ReparseState {
  [feedId: string]: FeedAsyncState & { logs?: FeedLog[] };
}

// Async thunk for reparsing a feed
export const reparseFeed = createAsyncThunk(
  'reparse/reparseFeed',
  async (feedId: string) => {
    const response = await fetch(`/api/feeds/${feedId}/reparse`, { method: 'POST' });
    if (!response.ok) {
      let errorMsg = `HTTP ${response.status}`;
      try {
        const data = await response.json();
        if (data && data.error) errorMsg = data.error;
      } catch {}
      throw new Error(errorMsg);
    }
    return feedId;
  }
);

const initialState: ReparseState = {};

// Async thunk to fetch the status of a feed by its ID
export const fetchFeedStatus = createAsyncThunk(
  'reparse/fetchFeedStatus',
  async (feedId: string) => {
    const response = await axios.get(`/api/feeds/${feedId}`);
    const statusInt = response.data.status;
    const status = statusMap[statusInt] || 'error'; // fallback to 'error' if unknown
    return { feedId, status };
  }
);

// Async thunk to fetch logs for a specific feed
export const fetchFeedLogs = createAsyncThunk(
  'reparse/fetchFeedLogs',
  async (feedId: string) => {
    const response = await axios.get(`/api/feeds/${feedId}`);
    // Adjust this if your logs are under a different key
    return { feedId, logs: response.data.recent_logs || [] };
  }
);

const reparseSlice = createSlice({
  name: 'reparse',
  initialState,
  reducers: {
    //Sets "Pending" status while being reparsed
    startReparse: (state, action: PayloadAction<string>) => {
      if (!state[action.payload]) {
        state[action.payload] = {
        status: 'pending',
        loading: false,
        reparsing: true,
        error: null,
        success: false,
        logs: [],
      };
      } else {
        state[action.payload].status = 'pending';
        state[action.payload].reparsing = true;
        state[action.payload].error = null;
        state[action.payload].success = false;
      }
    },

    //Sets "Idle" state and start the api call to set the status from the DB
    finishReparse: (state, action: PayloadAction<string>) => {
      if (state[action.payload]) {
        state[action.payload].status = 'idle';
        state[action.payload].loading = false;
        state[action.payload].success = true;
      }
    },
    //Resets the reparse state for a specific feedId
    //This is useful if the reparse was cancelled or failed
    resetReparse: (state, action: PayloadAction<string>) => {
      delete state[action.payload];
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchFeedStatus.pending, (state, action) => {
        const feedId = action.meta.arg;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].loading = true;
        state[feedId].error = null;
        state[feedId].success = false;
      })
      .addCase(fetchFeedStatus.fulfilled, (state, action) => {
        const { feedId, status } = action.payload;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].status = status;
        state[feedId].loading = false;
        state[feedId].success = true;
      })
      .addCase(fetchFeedStatus.rejected, (state, action) => {
        const feedId = action.meta.arg;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].loading = false;
        state[feedId].error = action.error.message || 'Failed to fetch status';
        state[feedId].success = false;
      })
      .addCase(fetchFeedLogs.fulfilled, (state, action) => {
         const { feedId, logs } = action.payload;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false, logs: [] };
        state[feedId].logs = logs;
    });
  },
});

export const { startReparse, finishReparse, resetReparse } = reparseSlice.actions;
export default reparseSlice.reducer;
