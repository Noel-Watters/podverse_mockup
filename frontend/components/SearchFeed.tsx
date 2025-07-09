import React from "react";

interface SearchFeedsProps {
  searchTerm: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
}

const SearchFeeds: React.FC<SearchFeedsProps> = ({
  searchTerm,
  onSearchChange,
  placeholder = "Search feeds...",
}) => (
  <input
    type="text"
    placeholder={placeholder}
    className="rounded-full px-5 py-2 w-1/2 bg-white text-black placeholder-gray-400 focus:outline-none border border-gray-300"
    value={searchTerm}
    onChange={onSearchChange}
  />
);

export default SearchFeeds;

