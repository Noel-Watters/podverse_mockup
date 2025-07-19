"use client";
import React from "react";

interface SearchFeedsProps {
  searchTerm: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  onSearchSubmit?: () => void;
}

function SearchFeeds({ searchTerm, onSearchChange, placeholder, onSearchSubmit }: SearchFeedsProps) {
  return (
    <form onSubmit={e => { e.preventDefault(); onSearchSubmit && onSearchSubmit(); }} className="w-full justify-center flex">
      <input
        type="text"
        placeholder={placeholder}
        className="rounded-full px-5 py-2 w-1/2 bg-white text-black placeholder-gray-400 focus:outline-none border border-gray-300"
        value={searchTerm}
        onChange={onSearchChange}
      />
    </form>
  );
}

export default SearchFeeds;
