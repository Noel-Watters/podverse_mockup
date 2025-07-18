"use client";
import React, {useState} from "react";
import {FunnelIcon, ArrowsUpDownIcon, ArrowDownTrayIcon, FlagIcon } from "@heroicons/react/24/outline";
import ReparseButton from "../reparsefeed/ReparseButton";
import { Feed } from "@/types/feed";

interface FeedToolbarProps {
  feeds:Feed[];
  onSortChange: (sort: string) => void;
  onOrderChange: (order: string) => void;
  onFilterChange: (filter: string, value: string) => void;
  selectedFeeds: number[]; 
  setSelectedFeeds: (ids: number[]) => void;
  onBulkReparse: () => void;
  onBulkUpdateStatus: (newStatus: string) => void;
  isBulkReparseLoading: boolean;
}



export default function FeedToolBar({ 
  feeds,
  onSortChange, 
  onOrderChange, 
  onFilterChange,
  selectedFeeds,
  onBulkReparse,
  onBulkUpdateStatus,
  isBulkReparseLoading,
  setSelectedFeeds,
}: FeedToolbarProps) {
  const statusMap = { flagged: 1, unflagged: 2, disabled: 3 };
  type StatusKey = keyof typeof statusMap;
  const [statusToUpdate, setStatusToUpdate] = useState<StatusKey>("flagged");
  const [error, setError] = useState<string>("");
  const [exportFormat, setExportFormat] = useState("csv");
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const [isParsing, setIsParsing] = useState<boolean>(false);

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
    <div className="flex flex-col pt-2 w-full "> {/* Container */}
    <div className="flex flex-col  w-full"> {/* Col 1 */}
      {/* Top Row: Sort & Filter controls */}
      <div className="flex flex-row flex-wrap w-full"> {/* Header Row*/}

        <div className="flex px-2 ">
            <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              
              checked={feeds.length > 0 && selectedFeeds.length === feeds.length}
              className="peer appearance-none h-7 w-7 rounded-md bg-[var(--pv-cream)] border border-black checked:bg-black checked:border-black focus:outline-none" 
              onChange={e => setSelectedFeeds(e.target.checked ? feeds.map(f => f.id) : [])}
            />
            <svg
              className="absolute w-4 h-4 text-[var(--pv-cream)] pointer-events-none left-0.5 top-0.5 opacity-0 peer-checked:opacity-100 transition"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              viewBox="0 0 24 24"
              >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </label>
            
        </div>


        <div className="flex flex-row py-1 gap-2">        {/* Row one*/}
        {/* Sort by */}
        <div className="relative">
          <select onChange={(e) => onSortChange(e.target.value)}
            className="appearance-none border border-black rounded-md px-2 py-1 w-32 text-left text-sm text-black focus:outline-none min-w-[90px] h-8"
            defaultValue=""
          >
            <option value="">Sort by</option>
            <option value="updated_at">Last Updated</option>
            <option value="id">Feed ID</option>
            <option value="url">Feed URL</option>
          </select>
          <ArrowsUpDownIcon className="h-4 w-4 absolute right-1 top-2 text-black pointer-events-none" />
        </div>
        {/* Status */}
        <div className="relative">
          <select onChange={e => onFilterChange('status', e.target.value)}
            className="appearance-none border border-black rounded-md w-32 px-4 py-1 text-left text-sm text-black bg-white focus:outline-none min-w-[90px] h-8"
            defaultValue=""
          >
            <option value="">Flag Statuses</option>
            <option value="active">Active </option>
            <option value="always-parse">Always Parse</option>
            <option value="spam">Spam</option>
            <option value="takedown">Take Down</option>
            <option value="pending-archive">Pending</option>
            <option value="fetch_error">Fetch Error</option>
            <option value="parse_error">Parse Error</option>
            <option value="archived">Archived</option>
          </select>
          <FunnelIcon className="h-4 w-4 absolute right-1 top-2 text-black pointer-events-none" />
        </div>
        {/* Priorities */}
        <div className="relative">
          <select onChange={e => onFilterChange('parsing_priority', e.target.value)}
            className="appearance-none w-32 text-left border border-black rounded-md px-2 py-1 text-sm text-black bg-white focus:outline-none min-w-[90px] h-8"
            defaultValue=""
          >
            <option value="">All Priorities</option>
            <option value="1">Very Low</option>
            <option value="2">Low</option>
            <option value="3">Medium</option>
            <option value="4">High</option>
            <option value="5">Very High</option>
          </select>
          <FunnelIcon className="h-4 w-4 absolute right-1 top-2 text-black pointer-events-none" />
          </div>
        </div>
        <div className="flex ml-20 gap-2 "> {/* Row two*/}
        {/* Parsing Toggle */}
        <button
          type="button"
          className={`rounded-full px-4 py-1 text-sm border h-8 transition ${isParsing ? 'bg-primary text-white border-border' : 'bg-white text-black border-black'}`}
          onClick={() => { setIsParsing(!isParsing); onFilterChange('is_parsing', (!isParsing).toString()); }}
        >
          Parsing
        </button>
        {/* Asc/Desc Toggle Button */}
        <button
          type="button"
          className={`rounded-full px-4 py-1 text-sm border h-8 transition ${order === 'asc' ? 'bg-primary text-white border-border' : 'bg-white text-black border-black'}`}
          onClick={() => {
            const newOrder = order === 'asc' ? 'desc' : 'asc';
            setOrder(newOrder);
            onOrderChange(newOrder);
          }}
        >
          {order === 'asc' ? 'Ascending' : 'Descending'}
        </button>
        </div>


      {/* Right: Bulk Operations and Add new feed */}
      <div className="flex flex-col items-right ml-auto gap-1">
        <div className="flex gap-2 items-end">
          {/* Bulk Update Status */}
          <button
            onClick={() => onBulkUpdateStatus(statusMap[statusToUpdate].toString())}
            disabled={selectedFeeds.length === 0}
            className="border border-black bg-white text-black rounded-md w-9 h-9 flex items-center justify-center hover:bg-gray-100 transition"
            aria-label="Confirm Status Update"
          >
            <FlagIcon className="h-5 w-5 text-black" />
          </button>
          <select
            value={statusToUpdate}
            onChange={e => setStatusToUpdate(e.target.value as StatusKey)}
            className="border border-black rounded-md px-2 py-1 text-sm text-black bg-white focus:outline-none min-w-[90px] mr-2 h-9"
          >
            <option value="flagged">Flagged</option>
            <option value="unflagged">Unflagged</option>
            <option value="disabled">Disabled</option>
          </select>
          
          {/* Bulk Reparse Button */}
          <ReparseButton
            onClick={onBulkReparse}
            loading={isBulkReparseLoading}
            disabled={selectedFeeds.length === 0}
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
            className="border border-black rounded-md px-2 py-1 h-9 text-sm text-black bg-white focus:outline-none min-w-[90px] mr-2"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </div>
      </div>
    </div>
    </div>
          </div>
  );
}
