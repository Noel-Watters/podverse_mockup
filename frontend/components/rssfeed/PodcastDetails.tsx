import React from "react";
import { Feed } from "@/types/feed";
import { Channel } from "@/types/channel";
import { RssIcon } from "@heroicons/react/24/outline";

interface PodcastDetailsProps {
  feed: Feed;
  channel: Channel;
}

const priorityMap = [
  "No Priority",
  "Very Low",
  "Low",
  "Medium",
  "High",
  "Very High"
];

const PodcastDetails: React.FC<PodcastDetailsProps> = ({ feed, channel }) => {
  // Defensive: categories
  const categories = channel && Array.isArray((channel as any).categories) ? (channel as any).categories : [];
  return (
    <div className="p-4 w-full bg-white">
      <p className="text-muted text-xs">Index ID: {channel?.podcast_index_id ?? "-"} </p>
      <div className="flex flex-col md:flex-row gap-4 w-full">
        {/* First Row */}
        <div className="flex flex-col border border-gray-400 rounded-lg p-3 flex-1 min-h-[80px] justify-center">
          <span className="text-muted text-sm flex items-center gap-2">
            <RssIcon className="h-4 w-4 text-muted" /> RSS Feed
          </span>
          <span className="text-s break-all">{feed.url}</span>
        </div>
        <div className="flex flex-col border border-gray-400 rounded-lg p-3 flex-1 min-h-[80px] justify-center">
          <span className="text-muted text-sm">Parsing Priority</span>
          <span className="text-base">{priorityMap[feed.parsing_priority ?? 0]}</span>
        </div>
      </div>
      <div className="flex flex-col md:flex-row gap-4 w-full mt-4">
        {/* Second Row */}
        <div className="flex flex-col border border-gray-400 rounded-lg p-3 flex-1 min-h-[80px] justify-center">
          <span className="text-muted text-sm">Categories</span>
          <span className="text-base">
            {categories.length > 0
              ? categories.map((cat: any) => cat.display_name).join(", ")
              : "-"}
          </span>
        </div>
        <div className="flex flex-col border border-gray-400 rounded-lg p-3 flex-1 min-h-[80px] justify-center">
          <span className="text-muted text-sm">Medium</span>
          <span className="text-base">{
            channel && channel.medium && typeof channel.medium === "object"
              ? channel.medium.value ?? "-"
              : (channel && typeof channel.medium === "string" ? channel.medium : "-")
          }</span>
        </div>
      </div>
    </div>
  );
};

export default PodcastDetails;
