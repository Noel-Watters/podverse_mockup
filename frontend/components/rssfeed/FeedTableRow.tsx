"Use Client";
import React from "react";
import FeedStatusBadge from "./FeedStatusBadge";
import ReparseFeed from "@/components/reparsefeed/ReparseFeed";
import ReparseButton from "@/components/reparsefeed/ReparseButton";
import { Feed } from "@/types/feed";

interface FeedTableRowProps {
  feed: Feed;
  expanded: boolean;
  onExpand: () => void;
  onNotify: (n: {
    type: "success" | "error";
    message: string;
    duration?: number;
    details?: string[];
  }) => void;
}

const FeedTableRow: React.FC<FeedTableRowProps> = ({
  feed,
  expanded,
  onExpand,
  onNotify,
}) => (
  <tr className="border-t border-podverse-border hover:bg-podverse-highlight transition">
    <td className="px-4 py-2 font-medium">{feed.id}</td>
    <td className="px-4 py-2 truncate max-w-xs">{feed.url}</td>
    <td className="px-4 py-2">
      <FeedStatusBadge feed={feed} />
    </td>
    <td className="px-4 py-2">{feed.parsing_priority}</td>
    <td className="px-4 py-2 text-xs">
      {new Date(feed.created_at).toLocaleString()}
    </td>
    <td className="px-4 py-2 text-xs">
      {new Date(feed.updated_at).toLocaleString()}
    </td>
    <td className="px-4 py-2 text-sm">
      <button
        className="text-podverse-accent hover:underline text-xs"
        onClick={onExpand}
      >
        {expanded ? "Hide Log" : "View Log"}
      </button>
    </td>
    <td className="px-4 py-2">
      <ReparseFeed feedId={feed.id.toString()} onNotify={onNotify}>
        {({ onReparse, loading, status }) => (
          <ReparseButton
            onClick={onReparse}
            loading={loading}
            status={status}
          />
        )}
      </ReparseFeed>
    </td>
  </tr>
);

export default FeedTableRow;