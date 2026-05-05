"use client";
import React from "react";
import { BellIcon } from "@heroicons/react/24/outline";
import SearchFeeds from "./SearchFeed";

interface TopBarProps {
  searchValue: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onLogout: () => void;
  onNotificationsClick?: () => void;
  placeholder?: string;
  onSearchSubmit?: () => void;
}

function TopBar({ searchValue, onSearchChange, onLogout, onNotificationsClick, placeholder, onSearchSubmit }: TopBarProps) {


  return (
    <header className="flex justify-between pr-4 bg-bar items-center py-1">
      <div className="flex-1 flex justify-center">
        <SearchFeeds
          searchTerm={searchValue}
          onSearchChange={onSearchChange}
          placeholder={placeholder || "Search feeds..."}
          onSearchSubmit={onSearchSubmit}
        />
      </div>
      <div className="flex items-center space-x-4 ml-4">

        <button
          onClick={onLogout}
          className="py-2 px-6 bg-primary border border-border hover:bg-accent text-white rounded-md transition"
        >
          Logout
        </button>
      </div>
    </header>
  );
}

export default TopBar;