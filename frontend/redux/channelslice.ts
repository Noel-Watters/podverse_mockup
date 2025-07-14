
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { Channel } from '@/types/channel'; 


// State for all channels, keyed by feedId
interface ChannelState {
  data: { [feedId: string]: Channel | undefined };
  loading: { [feedId: string]: boolean };
  error: { [feedId: string]: string | null };
}

const initialState: ChannelState = {
  data: {},
  loading: {},
  error: {},
};

// Async thunk to fetch channel info by feedId
export const fetchChannelByFeedId = createAsyncThunk(
  'channel/fetchChannelByFeedId',
  async (feedId: string) => {
    const response = await axios.get(`/api/channels/${feedId}`);
    return { feedId, channel: response.data };
  }
);

const channelSlice = createSlice({
  name: 'channel',
  initialState,
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(fetchChannelByFeedId.pending, (state, action) => {
        state.loading[action.meta.arg] = true;
        state.error[action.meta.arg] = null;
      })
      .addCase(fetchChannelByFeedId.fulfilled, (state, action) => {
        const { feedId, channel } = action.payload;
        state.data[feedId] = channel;
        state.loading[feedId] = false;
        state.error[feedId] = null;
      })
      .addCase(fetchChannelByFeedId.rejected, (state, action) => {
        const feedId = action.meta.arg;
        state.loading[feedId] = false;
        state.error[feedId] = action.error.message || 'Failed to fetch channel';
      });
  },
});

export default channelSlice.reducer;
