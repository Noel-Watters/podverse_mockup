"use client";
import React from "react";
import FeedStatusBadge from "./FeedStatusBadge";
import ReparseFeed from "@/components/reparsefeed/ReparseFeed";
import ReparseButton from "@/components/reparsefeed/ReparseButton";
import { Feed } from "@/types/feed";
import { Channel } from "@/types/channel";

interface FeedTableRowProps {
  feed: Feed;
  channel: Channel;
  expanded: boolean;
  onExpand: () => void;
  onNotify: (n: {
    type: "success" | "error";
    message: string;
    duration?: number;
    details?: string[];
  }) => void;
  checkbox?: React.ReactNode;
}

const FeedTableRow: React.FC<FeedTableRowProps> = ({
  feed,
  channel,
  expanded,
  onExpand,
  onNotify,
  checkbox,
}) => (
  <div 
  onClick={onExpand}
  style={{ cursor: "pointer" }} 
  className={`grid grid-cols-[40px_1fr_125px__120px_120px_60px] gap-4 my-2 items-center rounded border border-border hover:bg-gray-300 transition${expanded ? " bg-accent" : ""}`}
  >

      {/* Checkbox */}
    <div>
      <p className="px-2" onClick={e => e.stopPropagation()}>{checkbox}</p>
    </div>


      {/* Feed Info */}
    <div>
      <p className="font-semibold">{channel?.title || feed.url}</p>
      <p className="text-xs text-muted">Feed ID: {feed.id}</p>
    </div>

      {/* Dates */}
    <div>
      <p className="px-4 py-2 text-xs">
        {new Date(feed.created_at ?? "").toLocaleString()}
      </p>
    </div>
    <div>
      <p className="px-4 py-2 text-xs">
        {new Date(feed.updated_at ?? "").toLocaleString()}
      </p>
    </div>

    {/* Feed Status */}
    <div>
      <FeedStatusBadge feed={feed} />
    </div>

    {/* Reparse Button */}
    <div>
      <ReparseFeed feedId={feed.id.toString()} onNotify={onNotify}>
        {({ onReparse, loading, status }) => (
          <span onClick = {e => e.stopPropagation()}>
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
);

export default FeedTableRow;