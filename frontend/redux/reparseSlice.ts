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

// Async thunk for individual reparsing a feed
export const reparseFeed = createAsyncThunk(
  'reparse/reparseFeed',
  async (feedId: string) => {
    const response = await axios.post(`/api/feeds/${feedId}/reparse`);
    if (!response.data.success) {
      let errorMsg = `HTTP ${response.status}`;
      try {
        const data = response.data;
        if (data && data.error) errorMsg = data.error;
      } catch {}
      throw new Error(errorMsg);
    }
    return feedId;
  }
);

// Async thunk for bulk reparsing a feed
export const bulkReparseFeeds = createAsyncThunk(
  'reparse/bulkReparseFeeds',
  async (feedIds: number[]) => {
    const response = await axios.post('/api/feeds/bulk-reparse', {
      feed_ids: feedIds,
    });
    if (!response.data.success) throw new Error('Bulk reparse failed');
    return feedIds;
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
    const response = await axios.get(`/api/feeds/${feedId}/logs`);
    // Adjust this if your logs are under a different key
    return { feedId, logs: response.data.logs || [] };
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
        state[action.payload].reparsing = false; 
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
          .addCase(reparseFeed.pending, (state, action) => {
        const feedId = action.meta.arg;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].loading = true;
        state[feedId].reparsing = true;
        state[feedId].error = null;
        state[feedId].success = false;
        state[feedId].status = 'pending';
      })
      .addCase(reparseFeed.fulfilled, (state, action) => {
        const feedId = action.payload;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].loading = false;
        state[feedId].reparsing = false;
        state[feedId].success = true;
        state[feedId].status = 'idle';
      })
      .addCase(reparseFeed.rejected, (state, action) => {
        const feedId = action.meta.arg;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].loading = false;
        state[feedId].reparsing = false;
        state[feedId].error = action.error.message || 'Reparse failed';
        state[feedId].success = false;
        state[feedId].status = 'error';
      })
    // Handle individual feed reparsing
      .addCase(fetchFeedStatus.pending, (state, action) => {
        const feedId = action.meta.arg;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].loading = true;
        state[feedId].error = null;
        state[feedId].reparsing = true;
        state[feedId].success = false;
      })
      .addCase(fetchFeedStatus.fulfilled, (state, action) => {
        const { feedId, status } = action.payload;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].status = 'idle';
        state[feedId].loading = false;
        state[feedId].reparsing = false;
        state[feedId].success = true;
      })
      .addCase(fetchFeedStatus.rejected, (state, action) => {
        const feedId = action.meta.arg;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false };
        state[feedId].loading = false;
        state[feedId].reparsing = false;
        state[feedId].error = action.error.message || 'Failed to fetch status';
        state[feedId].success = false;
      })
      // Fetch logs for a specific feed
      .addCase(fetchFeedLogs.fulfilled, (state, action) => {
        const { feedId, logs } = action.payload;
        if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false, logs: [] };
        state[feedId].logs = logs;
        console.log('Redux logs updated for feed', feedId, logs);
      })
      // Bulk reparse state handling
      .addCase(bulkReparseFeeds.pending, (state, action) => {
        const feedIds = action.meta.arg;
        feedIds.forEach(feedId => {
          if (!state[feedId]) {
            state[feedId] = { status: 'pending', loading: false, reparsing: true, error: null, success: false, logs: [] };
          } else {
            state[feedId].status = 'pending';
            state[feedId].reparsing = true;
            state[feedId].error = null;
            state[feedId].success = false;
          }
        });
      })
      .addCase(bulkReparseFeeds.fulfilled, (state, action) => {
        const feedIds = action.payload;
        feedIds.forEach(feedId => {
          if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false, logs: [] };
          state[feedId].status = 'idle';
          state[feedId].reparsing = false;
          state[feedId].success = true;
        });
      })
      .addCase(bulkReparseFeeds.rejected, (state, action) => {
        const feedIds = action.meta.arg;
        feedIds.forEach(feedId => {
          if (!state[feedId]) state[feedId] = { status: 'idle', loading: false, error: null, success: false, logs: [] };
          state[feedId].reparsing = false;
          state[feedId].status = 'idle';
          state[feedId].error = action.error.message || 'Bulk reparse failed';
          state[feedId].success = false;
        });
    });
  },
});

export const { startReparse, finishReparse, resetReparse } = reparseSlice.actions;
export default reparseSlice.reducer;
