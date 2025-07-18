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
      // Integer status code mapping
      const statusMap: Record<string, { label: string; className: string }> = {
        "active":           { label: "Active",     className: "bg-green-500 text-white" },
        "always-parse":     { label: "Always Parse",className: "bg-green-500 text-white" },
        "spam":             { label: "Spam",  className: "bg-yellow-400 text-white" },
        "pending-archive":  { label: "Pending Archive",  className: "bg-yellow-400 text-blue-900" },
        "archived":         { label: "Archived", className: "bg-gray-500 text-white" },
        "takedown":         { label: "Takedown",  className: "bg-yellow-400 text-white" },
        "parse_error":      { label: "Parse Error",    className: "bg-red-400 text-black" },
        "fetch_error":      { label: "Fetch Error",    className: "bg-red-400 text-white" },
        // fallback
        "":                  { label: "Unknown", className: "bg-gray-300 text-black" }
      };
      const status = feed.flag_status ?? "";
      const { label, className } = statusMap[status] || statusMap[""];

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