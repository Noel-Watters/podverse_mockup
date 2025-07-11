"Use Client";
import React from "react";
import { Feed, FeedLog } from "@/types/feed";

interface FeedAuditLogRowProps {
  feed: Feed;
  logLoading: boolean;
  logError: string | null;
  handleCopyLogs: (logs: FeedLog[]) => void;
  handleDownloadLogs: (logs: FeedLog[], title: string) => void;
}

const FeedAuditLogRow: React.FC<FeedAuditLogRowProps> = ({
  feed,
  logLoading,
  logError,
  handleCopyLogs,
  handleDownloadLogs,
}) => (
  <tr className="bg-podverse-surface">
    <td colSpan={8} className="px-6 py-3 border-t border-podverse-border">
      <div>
        <h3 className="font-semibold text-sm text-podverse-text mb-2">
          Audit Log
        </h3>
        <div className="flex flex-col gap-2 mb-4 max-h-60 overflow-y-auto bg-gray-50 rounded p-2">
          {logLoading ? (
            <div className="text-podverse-muted">Loading logs...</div>
          ) : logError ? (
            <div className="text-red-500">{logError}</div>
          ) : !feed.logs || feed.logs.length === 0 ? (
            <div className="text-podverse-muted">No logs available</div>
          ) : (
            feed.logs.map((log, i) => (
              <div key={i} className="text-xs border-b border-gray-200 py-2">
                <div>
                  <strong>Time:</strong>{" "}
                  {new Date(
                    log.last_finished_parse_time ||
                    log.finished_at ||
                    log.started_at ||
                    ""
                  ).toLocaleString()}
                </div>
                <div>
                  <strong>Status:</strong>{" "}
                  <span className={log.parse_errors === 0 ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
                    {log.parse_errors === 0 ? "Live" : "Error"}
                  </span>
                </div>
                <div>
                  <strong>HTTP Status:</strong> {log.http_status ?? "N/A"}
                </div>
                <div>
                  <strong>Message:</strong> {log.parse_error_message ?? ""}
                </div>
                <div>
                  <strong>Parsed By:</strong> {log.parsed_by ?? ""}
                </div>
              </div>
            ))
          )}
        </div>
        <div className="space-x-2">
          <button
            className="text-xs bg-podverse-surface px-2 py-1 rounded hover:bg-podverse-highlight text-podverse-accent"
            onClick={() => handleCopyLogs(feed.logs ?? [])}
            disabled={!feed.logs || feed.logs.length === 0}
          >
            Copy Log
          </button>
          <button
            className="text-xs bg-podverse-surface px-2 py-1 rounded hover:bg-podverse-highlight text-podverse-accent"
            onClick={() => handleDownloadLogs(feed.logs ?? [], feed.id.toString())}
            disabled={!feed.logs || feed.logs.length === 0}
          >
            Download Log
          </button>
        </div>
      </div>
    </td>
  </tr>
);

export default FeedAuditLogRow;