// features/feeds/feedsSlice.ts
import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { Feed } from '@/types/feed'; 



interface FeedState {
  items: Feed[];
  offset: number;
  limit: number;
  loading: boolean;
  hasMore: boolean;
  error?: string;
}

const initialState: FeedState = {
  items: [],
  offset: 0,
  limit: 25,
  loading: false,
  hasMore: true,
};

export const fetchFeeds = createAsyncThunk<Feed[], number>(
  'feeds/fetchFeeds',
  async (offset, { rejectWithValue }) => {
    try {
      const response = await axios.get(`/api/feeds/?limit=25&offset=${offset}`);
      return response.data ?? [];
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);


const feedsSlice = createSlice({
  name: 'feeds',
  initialState,
  reducers: {
    resetFeeds(state) {
      state.items = [];
      state.offset = 0;
      state.hasMore = true;
      state.loading = false;
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchFeeds.pending, state => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchFeeds.fulfilled, (state, action: PayloadAction<Feed[]>) => {
        const newFeeds = action.payload;
        state.items.push(...newFeeds);
        state.offset += state.limit;
        state.hasMore = newFeeds.length === state.limit;
        state.loading = false;
      })
      .addCase(fetchFeeds.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { resetFeeds } = feedsSlice.actions;
export default feedsSlice.reducer;
