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
        "active":      { label: "Active",    className: "bg-green-600 text-white" },
        "live":        { label: "Live",      className: "bg-green-600 text-white" },
        "pending":     { label: "Pending",   className: "bg-blue-500 text-white" },
        "error":       { label: "Error",     className: "bg-red-500 text-white" },
        "flagged":     { label: "Flagged",   className: "bg-yellow-500 text-black" },
        "archived":    { label: "Archived",  className: "bg-gray-500 text-white" },
        "fetch_error": { label: "Fetch Error", className: "bg-red-400 text-white" },
        "parse_error": { label: "Parse Error", className: "bg-yellow-400 text-black" },
        "always-parse":{ label: "Always Parse", className: "bg-purple-500 text-white" },
        "pending-archive": { label: "Pending Archive", className: "bg-blue-200 text-blue-900" },
        "spam":            { label: "Spam",            className: "bg-pink-500 text-white" },
        "takedown":        { label: "Takedown",        className: "bg-black text-white" },
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