"use client";
import React from "react";
import ReparseFeed from "@/components/reparsefeed/ReparseFeed";
import { Feed, FEED_STATUS_MAP } from "@/types/feed";


interface FeedStatusBadgeProps {
  feed: Feed;
}

const FeedStatusBadge: React.FC<FeedStatusBadgeProps> = ({ feed }) => (
  <ReparseFeed feedId={feed.id.toString()}>
    {() => {
      const status = feed.flag_status ?? "";
      const { label, className } = FEED_STATUS_MAP[status] || FEED_STATUS_MAP[""];
      return (
        <span
          className={`flex items-center justify-center w-24 px-0 py-1 rounded-full shadow-md text-sm font-semibold select-none ${className}`}
        >
          {label}
        </span>
      );
    }}
  </ReparseFeed>
);

export default FeedStatusBadge;