"Use Client";
import React from "react";
import FeedTableRow from "./FeedTableRow";
import FeedAuditLogRow from "./FeedAuditLogRow";
import { Feed, FeedLog } from "@/types/feed";
import { useSelector } from "react-redux";
import { RootState } from "@/redux/store";

interface FeedTableProps {
  feeds: Feed[];
  expandedFeedId: number | null;
  toggleExpand: (feedId: number) => void;
  // You can remove logLoading and logError from props if you only use Redux!
  handleCopyLogs: (logs: FeedLog[]) => void;
  handleDownloadLogs: (logs: FeedLog[], title: string) => void;
  onNotify: (n: {
    type: "success" | "error";
    message: string;
    duration?: number;
    details?: string[];
  }) => void;
}

const FeedTable: React.FC<FeedTableProps> = ({
  feeds,
  expandedFeedId,
  toggleExpand,
  handleCopyLogs,
  handleDownloadLogs,
  onNotify,
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
      {feeds.map((feed) => {
        // Get logs, loading, and error for this feed from Redux
        const logs = useSelector((state: RootState) => state.reparse[String(feed.id)]?.logs ?? []);
        const logLoading = useSelector((state: RootState) => state.reparse[String(feed.id)]?.loading ?? false);
        const logError = useSelector((state: RootState) => state.reparse[String(feed.id)]?.error ?? null);

        return (
          <React.Fragment key={feed.id}>
            <FeedTableRow
              feed={feed}
              expanded={expandedFeedId === feed.id}
              onExpand={() => toggleExpand(feed.id)}
              onNotify={onNotify}
            />
            {expandedFeedId === feed.id && (
              <FeedAuditLogRow
                feed={{ ...feed, logs }} // override logs with Redux logs
                logLoading={logLoading}
                logError={logError}
                handleCopyLogs={handleCopyLogs}
                handleDownloadLogs={handleDownloadLogs}
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

export default FeedTable;