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
  searchTerm:string;
}

const initialState: FeedState = {
  items: [],
  offset: 0,
  limit: 50,
  loading: false,
  filters: {
    status: "",
    parsing_priority: undefined,
    is_parsing: undefined,
    sort_by: 'id', // Only allow: 'id', 'url', 'updated_at'
    sort_order: 'desc'
  },
  hasMore: true,
  searchTerm: "",
};



// Helper to build query params from filters and pagination
const buildQueryParams = (filters: FeedFilters, offset: number, limit: number, searchTerm: string) => {
  const params = new URLSearchParams();

  if (searchTerm && searchTerm.trim() !== "") {
    params.append('search', searchTerm.trim());
  }


  //Add Filters
  if (filters.status !== undefined && filters.status !== "")
    params.append('status', filters.status);
  if (filters.parsing_priority !== undefined)
    params.append('parsing_priority', filters.parsing_priority.toString());
  if (filters.is_parsing !== undefined)
    params.append('is_parsing', filters.is_parsing.toString());

  // Sort by and order
  const allowedSorts = ['id', 'url', 'updated_at'];
  const sortField = allowedSorts.includes(filters.sort_by ?? '') ? (filters.sort_by ?? 'id') : 'id';
  params.append('sort_by', sortField);
  params.append('sort_order', filters.sort_order ?? 'desc');
  //panigation params
  params.append('limit', limit.toString());
  const page = Math.floor(offset / limit) + 1;
  params.append('page', page.toString());
  //params.append('offset', offset.toString());

  return params.toString();
};

export const fetchFeeds = createAsyncThunk<
  { data: Feed[]; meta?: { total_items?: number; has_next?: boolean; [key: string]: any } },
  void,
  { state: { feeds: FeedState } }
>(
  'feeds/fetchFeeds',
  async (_, { getState, rejectWithValue }) => {
    const { offset, limit, filters, searchTerm } = getState().feeds;
    const queryString = buildQueryParams(filters, offset, limit, searchTerm);
    // Debug logging for frontend request
    try {
      const response = await axios.get(`/api/feeds?${queryString}`);
      // Debug logging for backend response
      // Handle both array and object response shapes
      let feeds, meta;
      if (Array.isArray(response.data)) {
        feeds = response.data;
        meta = undefined;
      } else {
        feeds = response.data.data;
        meta = response.data.meta;
        if (!Array.isArray(feeds) || typeof meta !== 'object') {
        }
      }
      return { data: feeds, meta };
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
      setSearchTerm(state, action: PayloadAction<string>) {
      state.searchTerm = action.payload;
    }
  },
  extraReducers: builder => {
    builder
      .addCase(fetchFeeds.pending, state => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchFeeds.fulfilled, (state, action: PayloadAction<{ data: Feed[], meta?: { total_items?: number, has_next?: boolean } }>) => {
        const { data, meta } = action.payload;
        console.log('Fetched feed IDs:', (data ?? []).map(f => f.id));
        console.log('[FEEDS] Pagination meta:', meta);
        console.log('[FEEDS] Current offset:', state.offset, 'Limit:', state.limit, 'HasMore:', state.hasMore);
        if (!Array.isArray(data)) {
          console.warn('[FEEDS] Payload data is not an array:', data);
          state.items = [];
          state.hasMore = false;
          state.loading = false;
          return;
        }
        if (state.offset === 0) {
          state.items = data ?? [];
        } else {
          const existingIds = new Set(state.items.map(feed => feed.id));
          const newFeeds = (data ?? []).filter(feed => !existingIds.has(feed.id));
          state.items.push(...newFeeds);
          console.log('All feed IDs in state:', state.items.map(f => f.id));
        }
        // Use meta for offset and hasMore if available
        if (meta && typeof meta.total_items === 'number') {
          state.offset += data.length;
          // If backend provides has_next, use it; else calculate
          if (typeof meta.has_next === 'boolean') {
            state.hasMore = meta.has_next;
          } else {
            state.hasMore = state.offset < meta.total_items && data.length === state.limit;
          }
        } else {
          // Fallback: use actual data length for offset
          state.offset += data.length;
          state.hasMore = (data ?? []).length === state.limit;
        }
        state.loading = false;
      })
      .addCase(fetchFeeds.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { resetFeeds, setFilters, setSearchTerm } = feedsSlice.actions;
export default feedsSlice.reducer;
