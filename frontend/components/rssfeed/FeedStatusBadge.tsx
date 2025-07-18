"use client";
import React from "react";
import ReparseFeed from "@/components/reparsefeed/ReparseFeed";
import { Feed } from "@/types/feed";

interface FeedStatusBadgeProps {
  feed: Feed;
}

const FeedStatusBadge: React.FC<FeedStatusBadgeProps> = ({ feed }) => (
  <ReparseFeed feedId={feed.id.toString()}>
    {() => {
      // Map all possible status values, including 'active'
      const statusMap: Record<string, { label: string; className: string }> = {
        "active":      { label: "Live",    className: "bg-green-500 text-white" },
        "always-parse":{ label: "Live", className: "bg-green-500 text-white" },
        "pending":     { label: "Pending",   className: "bg-blue-500 text-white" },
        "archived":    { label: "Archived",  className: "bg-gray-500 text-white" },
        "fetch_error": { label: "Error", className: "bg-red-400 text-white" },
        "parse_error": { label: "Error", className: "bg-red-400 text-black" },
        "pending-archive": { label: "Flagged", className: "bg-yellow-400 text-blue-900" },
        "spam":            { label: "Flagged",            className: "bg-yellow-400 text-white" },
        "takedown":        { label: "Flagged",        className: "bg-yellow-400 text-white" },
        // fallback
        "":            { label: "Unknown",   className: "bg-gray-300 text-black" }
      };

      const feedStatus = feed.flag_status ?? "";
      const { label, className } = statusMap[feedStatus] || statusMap[""];

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