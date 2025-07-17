"use client";
import React from "react";
import FeedTableRow from "./FeedTableRow";
import FeedAuditLogRow from "./FeedAuditLogRow";
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

  return (
    <table className="min-w-full bg-podverse-surface rounded shadow text-podverse-text text-sm">
      <thead className="bg-podverse-accent text-black">
        <tr>
          <th>
            {/* Select All Checkbox */}
            <input
              type="checkbox"
              checked={feeds.length > 0 && selectedFeeds.length === feeds.length}
              onChange={e => setSelectedFeeds(e.target.checked ? feeds.map(f => f.id) : [])}
              

            />
          </th>
          {["ID", "URL", "Status", "Priority", "Created At", "Updated At", "Action"].map((header) => (
            <th key={header} className="text-left px-4 py-2 font-semibold">
              {header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {feeds.map((feed, idx) => {
          const logs = reparse[String(feed.id)]?.logs ?? [];
          const logLoading = reparse[String(feed.id)]?.loading ?? false;
          const logError = reparse[String(feed.id)]?.error ?? null;

          if (expandedFeedId === feed.id) {
            console.log('FeedAuditLogRow props:', {
              feed: { ...feed, logs },
              logLoading,
              logError
            });
          }

          return (
            <React.Fragment key={feed.id + '-' + idx}>
              <FeedTableRow
                feed={feed}
                expanded={expandedFeedId === feed.id}
                onExpand={() => toggleExpand(feed.id)}
                onNotify={onNotify}
                checkbox={
                  <input
                    type="checkbox"
                    checked={selectedFeeds.includes(feed.id)}
                    onChange={e => handleCheckboxChange(feed.id, e.target.checked)}
                  />
                }
              />
              {expandedFeedId === feed.id && (
                <FeedAuditLogRow
                  feed={{ ...feed, logs }} 
                  logLoading={logLoading}
                  logError={logError}
                />
              )}
            </React.Fragment>
          );
        })}
        {feeds.length === 0 && (
          <tr>
            <td
              colSpan={8}
              className="text-center text-podverse-muted py-4"
            >
              No feeds found.
            </td>
          </tr>
        )}

      </tbody>
    </table>
  );
};

export default FeedTable;