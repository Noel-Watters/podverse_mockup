"use client";
import React from "react";
import FeedStatusBadge from "./FeedStatusBadge";
import ReparseFeed from "@/components/reparsefeed/ReparseFeed";
import ReparseButton from "@/components/reparsefeed/ReparseButton";
import { Feed } from "@/types/feed";
import { Channel } from "@/types/channel";
import HealthDuration from "./HealthDuration";
import FeedUpdated from "./FeedUpdated";
import Healthbadge from "./Healthbadge";
import { useSelector } from "react-redux";
import { RootState } from "@/redux/store";

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
}) => {

  const feedState = useSelector((state: RootState) => state.reparse[feed.id]);

  return (
    <div
      onClick={onExpand}
      style={{ cursor: "pointer" }}
      className={`grid grid-cols-[40px_1fr_100px_175px_140px_60px] gap-4 my-3 py-1 items-center bg-row rounded-lg border border-gray-300 hover:bg-accent transition${expanded ? " bg-accent" : ""}`}
    >

      {/* Checkbox */}
    <div>
      <p className="px-2" onClick={e => e.stopPropagation()}>{checkbox}</p>
    </div>


      {/* Feed Info */}
    <div>
      <p className="font-semibold text-base">{channel?.title || feed.url}</p>
      <p className="text-xs text-muted">Feed ID: {feed.id}</p>
    </div>

      {/* Dates */}
    <div>
        <HealthDuration recent_logs={(feed.recent_logs ?? []).map(log => ({
          ...log,
          finished_at: log.finished_at ?? "",
        }))} 
        />
    </div>
    <div>
        <FeedUpdated updated_at={feed.updated_at ?? ""} />
    </div>

    {/* Feed Status */}
    <div>
      <Healthbadge recent_logs={(feed.recent_logs ?? []).map(log => ({
        ...log,
        finished_at: log.finished_at ?? "",
        parse_errors: log.parse_errors ?? 0,
      }))}
        reparsing={feedState?.reparsing}
        flag_status={feedState?.flag_status ?? feed.flag_status}
      />
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
};

export default FeedTableRow;