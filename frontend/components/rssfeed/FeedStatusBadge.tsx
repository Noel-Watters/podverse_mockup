"use client";
import React from "react";
import ReparseFeed from "@/components/reparsefeed/ReparseFeed";
import { Feed } from "@/types/feed";

interface FeedStatusBadgeProps {
  feed: Feed;
}

const FeedStatusBadge: React.FC<FeedStatusBadgeProps> = ({ feed }) => (
  <ReparseFeed feedId={feed.id.toString()}>
    {({ status }) => {
      let badgeLabel = "Live";
      let badgeClass = "bg-green-600 text-white";
      if (status === "pending") {
        badgeLabel = "Pending";
        badgeClass = "bg-blue-500 text-white";
      } else if (status === "error" || feed.feed_flag_status_id === 3) {
        badgeLabel = "Error";
        badgeClass = "bg-red-500 text-white";
      } else if (feed.feed_flag_status_id === 2) {
        badgeLabel = "Flagged";
        badgeClass = "bg-yellow-500 text-black";
      }
      return (
        <span
          className={`flex items-center justify-center w-24 px-0 py-1 rounded-full shadow-md text-sm font-semibold select-none ${badgeClass}`}
        >
          {badgeLabel}
        </span>
      );
    }}
  </ReparseFeed>
);

export default FeedStatusBadge;