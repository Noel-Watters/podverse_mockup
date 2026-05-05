import React from "react";
import { formatLocal } from "@/utils/datetime";

interface FeedUpdatedProps {
  updated_at: string; // ISO date string
}


const FeedUpdated: React.FC<FeedUpdatedProps> = ({ updated_at }) => {
  if (!updated_at) return <span>-</span>;
  const formatted = formatLocal(updated_at);
  return (
    <div className="flex flex-col items-center border border-gray-400 rounded  h-11 w-36 py-1">
      <p className="text-xs text-muted">Last Updated</p>
      <span className="font-semibold" title={`Updated at ${new Date(updated_at).toLocaleString()}`}>{formatted}</span>
    </div>
  );
};

export default FeedUpdated;
