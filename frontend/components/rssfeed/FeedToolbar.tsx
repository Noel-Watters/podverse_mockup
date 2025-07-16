"use client";
import React, {useEffect, useState} from "react";
import {FunnelIcon, ArrowsUpDownIcon, ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import ReparseButton from "../reparsefeed/ReparseButton";

interface FeedToolbarProps {
  onSortChange: (sort: string) => void;
  onOrderChange: (order: string) => void;
  onFilterChange: (filter: string, value: string) => void;
}



export default function FeedToolBar({ onSortChange, onOrderChange, onFilterChange }: FeedToolbarProps) {
  const [feeds, setFeeds] = useState([]);
  const [error, setError] = useState<string>("");
  const [exportFormat, setExportFormat] = useState("csv");

  // Export feeds
const exportFeeds = async () => {
  try {
    const response = await fetch(`/api/feeds/export?format=${exportFormat}`);
    if (!response.ok) throw new Error("Failed to export feeds");
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `feeds_export.${exportFormat}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    setError("Failed to export feeds");
  }
};

  return (
    <div className="flex flex-wrap items-center justify-between px-2 bg-white border-b border-gray-200 rounded-t-md">
      {/* Left: Sort & Filter controls */}
      <div className="flex gap-3 items-center">
        <div className="relative">
          <select onChange={(e) => onSortChange(e.target.value)}
            className="border border-black rounded-md px-4 py-2 text-base text-black bg-white focus:outline-none min-w-[120px]"
            defaultValue=""
          >
            <option value="">Sort by</option>
            <option value="feed_flag_status_id">Status</option>
            <option value="updated_at">Last Updated</option>
            <option value="created_at">Created</option>
            <option value="parsing_priority">Priority</option>
            <option value="id">Feed ID</option>
          </select>
          <ArrowsUpDownIcon className="h-5 w-5 absolute right-2 top-2 text-black pointer-events-none" />
        </div>
        <div className="relative">
          <select onChange={(e) => onOrderChange(e.target.value)}
            className="border border-black rounded-md px-4 py-2 text-base text-black bg-white focus:outline-none min-w-[100px]"
            defaultValue="desc"
         >
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
          <ArrowsUpDownIcon className="h-5 w-5 absolute right-2 top-2 text-black pointer-events-none" />
        </div>
          <div className="relative">
          <select onChange={e => onFilterChange('feed_flag_status_id', e.target.value)}
            className="border border-black rounded-md px-4 py-2 text-base text-black bg-white focus:outline-none min-w-[120px]"
            defaultValue=""
          >
            <option value="">All Statuses</option>
            <option value="1">Flagged</option>
            <option value="2">Unflagged</option>
            <option value="3">Disabled</option>
          </select>
          <FunnelIcon className="h-5 w-5 absolute right-2 top-2 text-black pointer-events-none" />
        </div>
        <div className="relative">
          <select onChange={e => onFilterChange('parsing_priority', e.target.value)}
            className="border border-black rounded-md px-4 py-2 text-base text-black bg-white focus:outline-none min-w-[120px]"
            defaultValue=""
          >
            <option value="">All Priorities</option>
            <option value="1">High</option>
            <option value="2">Medium</option>
            <option value="3">Low</option>
          </select>
          <FunnelIcon className="h-5 w-5 absolute right-2 top-2 text-black pointer-events-none" />
        </div>
        <div className="relative">
          <select onChange={e => onFilterChange('is_parsing', e.target.value)}
            className="border border-black rounded-md px-4 py-2 text-base text-black bg-white focus:outline-none min-w-[120px]"
            defaultValue=""
          >
            <option value="">All</option>
            <option value="true">Currently Parsing</option>
            <option value="false">Not Parsing</option>
          </select>
          <FunnelIcon className="h-5 w-5 absolute right-2 top-2 text-black pointer-events-none" />
        </div>
      </div>

      {/* Right: Bulk Operations and Add new feed */}
      <div className="flex flex-col items-end gap-1">
        <span className="text-xs font-semibold text-black mb-1 self-center">Bulk Operations</span>
        <div className="flex gap-2 items-center">
          {/* Bulk Reparse Button */}
          <ReparseButton
            onClick={() => {}} // placeholder, replace with actual handler later
            loading={false} // Replace with actual loading state
            disabled
          />
          {/* Export Button*/}
          <button
            onClick={exportFeeds}
            type="button"
            className="border border-black bg-white text-black rounded-md w-9 h-9 flex items-center justify-center hover:bg-gray-100 transition"
            aria-label="Export"
          >
            <ArrowDownTrayIcon className="h-5 w-5" />
          </button>
                    <select
            value={exportFormat}
            onChange={e => setExportFormat(e.target.value)}
            className="border border-black rounded-md px-2 py-1 text-base text-black bg-white focus:outline-none min-w-[90px] mr-2"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </div>
      </div>
    </div>
  );
}
