import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { Channel } from '@/types/channel'; 


// State for all channels, keyed by feedId
interface ChannelState {
  data: { [feedId: string]: Channel[] | undefined };
  loading: { [feedId: string]: boolean };
  error: { [feedId: string]: string | null };
}


const initialState: ChannelState = {
  data: {},
  loading: {},
  error: {},
};


// Async thunk to fetch channels by feedId(s)
export const fetchChannelsByFeedIds = createAsyncThunk(
  'channel/fetchChannelsByFeedIds',
  async (feedIds: string[] | number[]) => {
    const ids = feedIds.join(',');
    const response = await axios.get(`/api/channels/by-feed?feed_ids=${ids}`);
    const grouped: { [feedId: string]: Channel[] } = {};
    response.data.data.forEach((channel: Channel) => {
      const fid = String(channel.feed_id);
      if (!grouped[fid]) grouped[fid] = [];
      grouped[fid].push(channel);
    });
    return { grouped, requested: feedIds };
  }
);


const batchChannelSlice = createSlice({
  name: 'batchChannel',
  initialState,
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(fetchChannelsByFeedIds.pending, (state, action) => {
        // Set loading for all requested feedIds
        action.meta.arg.forEach((fid: string | number) => {
          state.loading[String(fid)] = true;
          state.error[String(fid)] = null;
        });
      })
      .addCase(fetchChannelsByFeedIds.fulfilled, (state, action) => {
        const { grouped, requested } = action.payload;
        requested.forEach((fid: string | number) => {
          state.data[String(fid)] = grouped[String(fid)] || [];
          state.loading[String(fid)] = false;
          state.error[String(fid)] = null;
        });
      })
      .addCase(fetchChannelsByFeedIds.rejected, (state, action) => {
        action.meta.arg.forEach((fid: string | number) => {
          state.loading[String(fid)] = false;
          state.error[String(fid)] = action.error.message || 'Failed to fetch channels';
        });
      });
  },
});

export default batchChannelSlice.reducer;
