"use client";
import React, { useEffect, useState } from "react";
import ChannelHeader from "./ChannelHeader";
import ChannelStats from "./ChannelStats";
import EpisodeLogSection from "./EpisodeLogSection";
import { ChannelData } from "@/types/channel";
import ChannelStatsCharts from "./ChannelStatsChats";
import AdminLayout from "@/layouts/AdminLayout";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/redux/store";
import { resetFeeds, setSearchTerm } from "@/redux/feedSlice";
import { fetchFeeds } from "@/redux/feedSlice";
import { useDebounce } from "@/hooks/useDebounce";
import { useRouter } from "next/navigation";




export default function ChannelLayout({ data }: { data: ChannelData }) {
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const { filters } = useSelector((state: RootState) => state.feeds);
  const searchTerm = useSelector((state: RootState) => state.feeds.searchTerm);
  const [inputValue, setInputValue] = useState(searchTerm);
  const debouncedSearch = useDebounce(inputValue, 300);

  //Search Logic
  useEffect(() => {
    setInputValue(searchTerm);
  }, []);

  useEffect(() => {
    dispatch(setSearchTerm(debouncedSearch));
    dispatch(resetFeeds());
    dispatch(fetchFeeds());
    console.log('[DEBUG] Search triggered:', debouncedSearch);
  }, [debouncedSearch, dispatch, filters]);

  const handleSearch = () => {
  setTimeout(() => {
    router.push(`/rssfeed?search=${encodeURIComponent(searchTerm)}`);
  }, 200); // 200ms delay
};

  
  return (
      <AdminLayout
            searchValue={inputValue}
            onSearchChange={(e) => setInputValue(e.target.value)}
            onSearchSubmit={handleSearch}
      >
        <div className="p-4">
          <ChannelHeader data={data} />
          <ChannelStats stats={data.stats[0]} />
          <EpisodeLogSection items={data.items} logs={data.feed.recent_logs ?? []} />
          <ChannelStatsCharts stats={data.stats[0]} />
        </div>
      </AdminLayout>
  );
}
