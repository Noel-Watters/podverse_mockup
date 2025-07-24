"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import FeedLogTable from "@/components/FeedLogTable";
import RecentFlaggedFeed from "@/components/dashboard/RecentFlaggedFeed";


interface DashboardFeedSectionProps {
  feeds: any[];
  loading: boolean;
  error: string | null;
  selectedFeedId: number | null;
  onSelectFeed: (feedId: any, logs: any) => void;
  onNotify: (n: { type: "error" | "success"; message: string; duration?: number; details?: string[] }) => void;
}

export default function DashboardFeedSection({
  feeds,
  loading,
  error,
  selectedFeedId,
  onSelectFeed,
  onNotify,
}: DashboardFeedSectionProps) {
  const router = useRouter();
  // Find logs for the selected feed
  const selectedFeed = feeds.find(f => f.id === selectedFeedId);
  const selectedFeedLogs = selectedFeed?.recent_logs || [];
  // NOTE: For now, channel ids are the same as feed ids. Update to use channel_id when available.
  const selectedChannelId = selectedFeed?.id;

  return (
    <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="border rounded p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Recent Flagged Podcasts</h2>
        </div>
        <div className="space-y-2">
          <RecentFlaggedFeed
            feeds={feeds}
            loading={loading}
            error={error}
            onSelectFeed={onSelectFeed}
            selectedFeedId={selectedFeedId}
            onNotify={onNotify}
          />
        </div>
      </div>

      <div className="border rounded p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Feed Log</h2>
          <button
            className="px-3 py-1 bg-primary text-white text-sm rounded"
            onClick={() => {
              if (selectedChannelId) {
                router.push(`/channels/${selectedChannelId}`);
              }
            }}
            disabled={!selectedChannelId}
          >
            Channel Details
          </button>
        </div>
        <div className="space-y-2">
            <FeedLogTable logs={selectedFeedLogs} />
        </div>
      </div>
    </section>
  );
}
