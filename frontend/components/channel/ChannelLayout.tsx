"use client";
import ChannelHeader from "./ChannelHeader";
import ChannelStats from "./ChannelStats";
import EpisodeLogSection from "./EpisodeLogSection";
import { ChannelData } from "@/types/channel";
import ChannelStatsCharts from "./ChannelStatsChats";



export default function ChannelLayout({ data }: { data: ChannelData }) {
  console.log("Channel Stats Feed", data);
  return (
    <div className="p-6 space-y-8">
      <ChannelHeader data={data} />
      <ChannelStats stats={data.stats[0]} />
      <EpisodeLogSection items={data.items} logs={data.feed.recent_logs ?? []} />
      <ChannelStatsCharts stats={data.stats[0]} />

    </div>
  );
}
