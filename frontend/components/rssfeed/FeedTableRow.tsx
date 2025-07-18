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
  <tr 
  onClick={onExpand}
  style={{ cursor: "pointer" }} 
  className={`border-t border-podverse-border hover:bg-podverse-highlight transition${expanded ? " bg-podverse-highlight" : ""}`}
  >
    <td onClick={e => e.stopPropagation()}>{checkbox}</td>
    <td className="px-4 py-2 font-medium">{feed.id}</td>
    <td className="px-4 py-2 truncate max-w-xs">{channel?.title || feed.url}</td>
    <td className="px-4 py-2 truncate max-w-xs">{channel?.id || "-"}</td>

    <td className="px-4 py-2">
      <FeedStatusBadge feed={feed} />
    </td>
    <td className="px-4 py-2">{feed.parsing_priority}</td>
    <td className="px-4 py-2 text-xs">
      {new Date(feed.created_at ?? "").toLocaleString()}
    </td>
    <td className="px-4 py-2 text-xs">
      {new Date(feed.updated_at ?? "").toLocaleString()}
    </td>
    <td className="px-4 py-2">
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
    </td>
  </tr>
);

export default FeedTableRow;