"use client";
import React from "react";
import FeedTableRow from "./FeedTableRow";
import FeedAuditLogRow from "./FeedExpandedRow";
import { Feed } from "@/types/feed";
import { useSelector } from "react-redux";
import { RootState } from "@/redux/store";


interface FeedTableProps {
  feeds: Feed[];
  expandedFeedId: number | null;
  toggleExpand: (feedId: number) => void;
  onNotify: (n: {
    type: "success" | "error";
    message: string;
    duration?: number;
    details?: string[];
  }) => void;
  selectedFeeds: number[];
  setSelectedFeeds: (ids: number[]) => void;
  
}

const FeedTable: React.FC<FeedTableProps> = ({
  feeds,
  expandedFeedId,
  toggleExpand,
  onNotify,
  selectedFeeds,
  setSelectedFeeds,
}) => {
    const handleCheckboxChange = (feedId: number, checked: boolean) => {
    if (checked) {
      setSelectedFeeds([...selectedFeeds, feedId]);
    } else {
      setSelectedFeeds(selectedFeeds.filter(id => id !== feedId));
    }
  };
  // Get the entire reparse state once
  const reparse = useSelector((state: RootState) => state.reparse);
  const channelsByFeedId = useSelector((state: RootState) => state.batchChannel.data);

  return (
    <div className="min-w-full rounded text-black shadow text-sm">
      <div className= "px-2 gap-2">
        {feeds.map((feed, idx) => {
          const logs = reparse[String(feed.id)]?.logs ?? [];
          const logLoading = reparse[String(feed.id)]?.loading ?? false;
          const logError = reparse[String(feed.id)]?.error ?? null;
          const channels = channelsByFeedId[String(feed.id)] || [];
          const channel = channels[0]


          return (
            <React.Fragment key={feed.id + '-' + idx}>
              <FeedTableRow
                feed={feed}
                channel={channel}
                expanded={expandedFeedId === feed.id}
                onExpand={() => toggleExpand(feed.id)}
                onNotify={onNotify}
                checkbox={
                  <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="peer appearance-none h-5 w-5 rounded-md bg-[var(--pv-cream)] border border-black checked:bg-primary checked:border-black focus:outline-none" 
                    checked={selectedFeeds.includes(feed.id)}
                    onChange={e => handleCheckboxChange(feed.id, e.target.checked)}
                  />
                  <svg
                    className="absolute w-4 h-4 text-white pointer-events-none left-0.5 top-0.5 opacity-0 peer-checked:opacity-100 transition-opacity duration-200"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    viewBox="0 0 24 24"
                    >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  </label>
                }
              />
              {expandedFeedId === feed.id && (
                <FeedAuditLogRow logs={logs} feed={feed} channel={channel} />
              )}
            </React.Fragment>
          );
        })}
        {feeds.length === 0 && (
            <h2 className="text-center text-podverse-muted py-4" > No feeds found. </h2>
        )}
    </div>
    </div>
  );
};

export default FeedTable;