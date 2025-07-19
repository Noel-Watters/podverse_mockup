import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { Channel } from '@/types/channel';

// State for a single channel, keyed by channelId
interface SingleChannelState {
  data: { [channelId: string]: Channel | undefined };
  loading: { [channelId: string]: boolean };
  error: { [channelId: string]: string | null };
}

const initialState: SingleChannelState = {
  data: {},
  loading: {},
  error: {},
};

// Async thunk to fetch a channel by channelId
export const fetchChannelById = createAsyncThunk(
  'channel/fetchChannelById',
  async (channelId: string | number) => {
    const response = await axios.get(`/api/channels/${channelId}`);
    return { channelId, channel: response.data };
  }
);

const singleChannelSlice = createSlice({
  name: 'singleChannel',
  initialState,
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(fetchChannelById.pending, (state, action) => {
        state.loading[String(action.meta.arg)] = true;
        state.error[String(action.meta.arg)] = null;
      })
      .addCase(fetchChannelById.fulfilled, (state, action) => {
        const { channelId, channel } = action.payload;
        state.data[String(channelId)] = channel;
        state.loading[String(channelId)] = false;
        state.error[String(channelId)] = null;
      })
      .addCase(fetchChannelById.rejected, (state, action) => {
        const channelId = String(action.meta.arg);
        state.loading[channelId] = false;
        state.error[channelId] = action.error.message || 'Failed to fetch channel';
      });
  },
});

export default singleChannelSlice.reducer;