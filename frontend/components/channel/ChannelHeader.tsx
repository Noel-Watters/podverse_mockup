"use client";
import { CalendarIcon, RssIcon } from "@heroicons/react/24/outline";
import { ChannelData } from "@/types/channel";
import ReparseFeed from "../reparsefeed/ReparseFeed";
import ReparseButton from "../reparsefeed/ReparseButton";
import { ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import FeedStatusBadge from "@/components/rssfeed/FeedStatusBadge";
import Healthbadge from "@/components/rssfeed/Healthbadge";

type ChannelHeaderProps = {
  data: ChannelData;
  onNotify?: (n: any) => void;
};


export default function ChannelHeader({ data, onNotify }: ChannelHeaderProps) {
  return (
    <div className="border border-gray-300 p-6 rounded-xl shadow space-y-2">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-black">{data.title}</h1>
          <p className="text-sm ml-2 text-black">Podcast Index ID: {data.podcast_index_id}</p>
        </div>
            <div className="flex items-center space-x-2">
              <Healthbadge recent_logs={(data.feed.recent_logs ?? []).map(log => ({
              ...log,
              finished_at: log.finished_at ?? "",
              parse_errors: log.parse_errors ?? 0,
            }))} />
            <ReparseFeed feedId={data.feed.id.toString()} onNotify={onNotify}>
                {({ onReparse, loading, status }) => (
                <span onClick={e => e.stopPropagation()}>
                    <ReparseButton
                        onClick={onReparse}
                        loading={loading}
                        status={status}
                    />
                </span>
                )}
            </ReparseFeed>
          </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {data.categories.map((cat) => (
          <span key={cat.id} className="text-sm border border-gray-400 bg-gradient-to-b from-[rgba(255,255,255,0)] to-[rgba(153,153,153,0.5)]  px-2 py-3 rounded-lg">
          {cat.display_name}
          </span>
          ))}
        <span className="text-sm border border-gray-400 bg-gradient-to-b from-[rgba(255,255,255,0)] to-[rgba(153,153,153,0.5)]  px-2 py-3 rounded-lg">Medium: {data.medium.value}</span>
      </div>

      <div className="flex flex-col gap-y-2">
          
        <span className="text-xs flex border px-2 py-1 rounded border-gray-400  w-96 h-8 items-center">
          <CalendarIcon className="h-4 w-4 mr-1" />
          Launched: {data.feed.created_at ? new Date(data.feed.created_at).toLocaleDateString() : "-"}
        </span>
        <a href={data.feed.url} className="w-96 h-8 flex items-center text-black border px-2 py-1 rounded border-gray-400 text-xs">
          <RssIcon className="h-4 w-4 mr-1" />
          RSS {data.feed.url ? data.feed.url : "N/A"}
        </a>
        <FeedStatusBadge feed={data.feed} />

      </div>


    </div>
  );
}
