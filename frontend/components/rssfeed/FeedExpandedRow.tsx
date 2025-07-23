"use client";
import React from "react";
import { useRouter } from "next/navigation";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import { FeedLog } from "@/types/feed";
import FeedLogTable from "@/components/FeedLogTable";
import PodcastDetails from "@/components/rssfeed/PodcastDetails";

interface FeedAuditLogRowProps {
  logs: FeedLog[];
  feed: any;
  channel: any;
}

const FeedAuditLogRow: React.FC<FeedAuditLogRowProps> = ({ logs, feed, channel }) => (
  (() => {
    const router = useRouter();
    return (
      <div className="flex flex-row gap-10 px-2 py-2">
        <div className="flex-1">
          <div className="flex flex-row items-center justify-between mb-2">
            <h3 className="font-semibold text-lg">Podcast Details</h3>
            <button
              className="ml-2"
              title="Go to Channel Details"
              onClick={() => router.push(`/channels/${channel.id}`)}
              style={{ background: "none", border: "none", padding: 0, cursor: "pointer" }}
            >
              <ArrowTopRightOnSquareIcon className="h-5 w-5 text-gray-500 hover:text-primary transition" />
            </button>
          </div>
          <PodcastDetails feed={feed} channel={channel} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-lg mb-2"> Feed Log </h3>
          <FeedLogTable logs={logs} />
        </div>
      </div>
    );
  })()
);

export default FeedAuditLogRow;