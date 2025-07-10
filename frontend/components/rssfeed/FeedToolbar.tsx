import React from "react";
import { PlusIcon, TrashIcon, FunnelIcon, ArrowsUpDownIcon, ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import ReparseButton from "../reparsefeed/ReparseButton";

interface FeedToolbarProps {
  onAddFeed: () => void;
  // Future: onBulkReparse, onBulkDelete, onSortChange, onFilterChange, etc.
}

export default function FeedToolBar({ onAddFeed }: FeedToolbarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between px-2 bg-white border-b border-gray-200 rounded-t-md">
      {/* Left: Sort & Filter controls */}
      <div className="flex gap-3 items-center">
        <div className="relative">
          <select
            className="border border-black rounded-md px-4 py-2 text-base text-black bg-white focus:outline-none min-w-[120px]"
            disabled
          >
            <option>Sort by</option>
            <option>Name</option>
            <option>Status</option>
            <option>Last Updated</option>
          </select>
          <ArrowsUpDownIcon className="h-5 w-5 absolute right-2 top-2 text-black pointer-events-none" />
        </div>
        <div className="relative">
          <select
            className="border border-black rounded-md px-4 py-2 text-base text-black bg-white focus:outline-none min-w-[100px]"
            disabled
          >
            <option>Filter</option>
            <option>Active</option>
            <option>Errored</option>
            <option>Disabled</option>
          </select>
          <FunnelIcon className="h-5 w-5 absolute right-2 top-2 text-black pointer-events-none" />
        </div>
        {/* Page Size Control */}
        <div className="relative">
          <select
            className="border border-black rounded-md px-4 py-2 text-base text-black bg-white focus:outline-none min-w-[80px]"
            disabled
          >
            <option>25 / page</option>
            <option>10 / page</option>
            <option>50 / page</option>
            <option>100 / page</option>
          </select>
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
          {/* Delete Selected Button */}
          <button
            type="button"
            className="border border-black bg-white text-black rounded-md w-9 h-9 flex items-center justify-center hover:bg-gray-100 transition"
            disabled
            aria-label="Delete Selected"
          >
            <TrashIcon className="h-5 w-5" />
          </button>
          {/* Export Button*/}
          <button
            type="button"
            className="border border-black bg-white text-black rounded-md w-9 h-9 flex items-center justify-center hover:bg-gray-100 transition"
            disabled
            aria-label="Export"
          >
            <ArrowDownTrayIcon className="h-5 w-5" />
          </button>
          {/* Add New RSS Feed Button */}
          <button
            type="button"
            className="border border-black rounded-md p-1 bg-white hover:bg-gray-100 transition flex items-center justify-center"
            onClick={onAddFeed}
            aria-label="Add New RSS Feed"
          >
            <PlusIcon className="h-5 w-5 text-black" />
          </button>
        </div>
      </div>
    </div>
  );
}
