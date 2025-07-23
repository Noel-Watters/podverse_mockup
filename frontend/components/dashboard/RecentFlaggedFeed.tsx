"use client";
import React from "react";
import HealthDuration from "@/components/rssfeed/HealthDuration";
import Healthbadge from "@/components/rssfeed/Healthbadge";
import ReparseButton from "@/components/reparsefeed/ReparseButton";
import ReparseFeed from "@/components/reparsefeed/ReparseFeed";

interface RecentFlaggedFeedProps {
  channelMap?: Record<number, { title?: string }>;
  onSelectFeed?: (feedId: number, logs: any[]) => void;
  selectedFeedId?: number | null;
}

interface RecentFlaggedFeedProps {
  channelMap?: Record<number, { title?: string }>;
  onSelectFeed?: (feedId: number, logs: any[]) => void;
  selectedFeedId?: number | null;
  feeds: any[];
  loading?: boolean;
  error?: string | null;
  onNotify: (n: { type: "error" | "success"; message: string; duration?: number; details?: string[] }) => void;
}

const RecentFlaggedFeed: React.FC<RecentFlaggedFeedProps> = ({ channelMap, onSelectFeed, selectedFeedId, feeds, loading, error, onNotify }) => {

  // Only show the 6 most recent feeds
  const recentFeeds = feeds.slice(0, 6);

  // Always select the top feed if none is selected
  React.useEffect(() => {
    if (recentFeeds.length > 0 && (!selectedFeedId || !recentFeeds.some(f => f.id === selectedFeedId))) {
      onSelectFeed?.(recentFeeds[0].id, recentFeeds[0].recent_logs);
    }
  }, [recentFeeds, selectedFeedId, onSelectFeed]);

  return (
    <div className="bg-white rounded-lg p-6 shadow-md flex flex-col h-[600px]">
      <div className="flex-1 overflow-y-auto">
        {loading && <div className="text-center text-gray-400 py-8">Loading...</div>}
        {error && <div className="text-center text-red-400 py-8">{error}</div>}
        {!loading && !error && recentFeeds.length === 0 && (
          <div className="text-center text-gray-400 py-8">No flagged feeds found.</div>
        )}
        {!loading && !error && recentFeeds.map(feed => (
          <div
            key={feed.id}
            className={`flex justify-between items-center p-3 rounded mb-3 border cursor-pointer bg-gray-50 hover:bg-blue-50 transition ${feed.id === selectedFeedId ? "bg-blue-100 border-blue-400" : ""}`}
            onClick={() => onSelectFeed?.(feed.id, feed.recent_logs)}
          >
            {/* Feed Info */}
            <div>
              <p className="font-semibold text-base">{feed.channel_title || feed.url}</p>
              <p className="text-xs text-muted">Feed ID: {feed.id}</p>
            </div>
            <div className="flex items-center gap-2 ml-auto">
              <HealthDuration recent_logs={feed.recent_logs} />
              <Healthbadge recent_logs={feed.recent_logs} />
              <div>
                <ReparseFeed feedId={feed.id.toString()} onNotify={onNotify}>
                  {({ onReparse, loading, status }) => (
                    <span onClick={e => e.stopPropagation()}>
                      <ReparseButton
                        onClick={onReparse}
                        loading={loading}
                        status={status}
                      />
                    </span>
                  )}
                </ReparseFeed>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};


export default RecentFlaggedFeed;