"Use Client";
import React from "react";
import FeedTableRow from "./FeedTableRow";
import FeedAuditLogRow from "./FeedAuditLogRow";
import { Feed, FeedLog } from "@/types/feed";

interface FeedTableProps {
  feeds: Feed[];
  expandedFeedId: number | null;
  toggleExpand: (feedId: number) => void;
  logLoading: boolean;
  logError: string | null;
  handleCopyLogs: (logs: FeedLog[]) => void;
  handleDownloadLogs: (logs: FeedLog[], title: string) => void;
}

const FeedTable: React.FC<FeedTableProps> = ({
  feeds,
  expandedFeedId,
  toggleExpand,
  logLoading,
  logError,
  handleCopyLogs,
  handleDownloadLogs,
}) => (
  <table className="min-w-full bg-podverse-surface rounded shadow text-podverse-text text-sm">
    <thead className="bg-podverse-accent text-black">
      <tr>
        {["ID", "URL", "Status", "Priority", "Created At", "Updated At", "Details", "Action"].map((header) => (
          <th key={header} className="text-left px-4 py-2 font-semibold">
            {header}
          </th>
        ))}
      </tr>
    </thead>
    <tbody>
      {feeds.map((feed) => (
        <React.Fragment key={feed.id}>
          <FeedTableRow
            feed={feed}
            expanded={expandedFeedId === feed.id}
            onExpand={() => toggleExpand(feed.id)}
          />
          {expandedFeedId === feed.id && (
            <FeedAuditLogRow
              feed={feed}
              logLoading={logLoading}
              logError={logError}
              handleCopyLogs={handleCopyLogs}
              handleDownloadLogs={handleDownloadLogs}
            />
          )}
        </React.Fragment>
      ))}
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

export default FeedTable;