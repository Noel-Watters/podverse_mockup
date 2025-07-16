// features/feeds/feedsSlice.ts
import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { Feed, FeedFilters } from '@/types/feed'; 



interface FeedState {
  items: Feed[];
  offset: number;
  limit: number;
  loading: boolean;
  filters: FeedFilters;
  hasMore: boolean;
  error?: string;
}

const initialState: FeedState = {
  items: [],
  offset: 0,
  limit: 25,
  loading: false,
  filters: {
    feed_flag_status_id: undefined,
    parsing_priority: undefined,
    is_parsing: undefined,
    sort: 'updated_at',
    order: 'desc'
  },
  hasMore: true,
};

// Helper to build query params from filters and pagination
const buildQueryParams = (filters: FeedFilters, offset: number, limit: number) => {
  const params = new URLSearchParams();

  if (filters.feed_flag_status_id !== undefined)
    params.append('feed_flag_status_id', filters.feed_flag_status_id.toString());

  if (filters.parsing_priority !== undefined)
    params.append('parsing_priority', filters.parsing_priority.toString());

  if (filters.is_parsing !== undefined)
    params.append('is_parsing', filters.is_parsing.toString());

  params.append('sort', filters.sort ?? 'updated_at');
  params.append('order', filters.order ?? 'desc');

  params.append('limit', limit.toString());
  params.append('offset', offset.toString());

  return params.toString();
};

export const fetchFeeds = createAsyncThunk<Feed[], void, {state: {feeds: FeedState}}>(
  'feeds/fetchFeeds',
  async (_, { getState, rejectWithValue }) => {
    const { offset, limit, filters } = getState().feeds;
    const queryString = buildQueryParams(filters, offset, limit);
    try {
      const response = await axios.get(`/api/feeds/?${queryString}`);
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
    setFilters (state, action: PayloadAction<Partial<FeedFilters>>) {
        state.filters = { ...state.filters, ...action.payload };
        state.offset = 0; 
        state.items = []; 
        state.hasMore = true; 
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchFeeds.pending, state => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchFeeds.fulfilled, (state, action: PayloadAction<Feed[]>) => {
        if (state.offset === 0) {
          state.items = action.payload;
        } else {
            state.items.push(...action.payload);
        }
        state.offset += state.limit;
        state.hasMore = action.payload.length === state.limit;
        state.loading = false;
      })
      .addCase(fetchFeeds.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { resetFeeds, setFilters } = feedsSlice.actions;
export default feedsSlice.reducer;
