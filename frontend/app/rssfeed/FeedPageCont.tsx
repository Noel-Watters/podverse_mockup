"use client";
import React, { useState, useEffect } from "react";
import { Feed, FeedLog } from "@/types/feed";
import AdminLayout from "@/layouts/AdminLayout";
import { useSearchParams } from "next/navigation";
import AddRssFeedModal from "@/components/AddRssFeedModal";
import { PlusIcon } from "@heroicons/react/24/outline";
import FeedTable from "@/components/rssfeed/FeedTable";

export default function FeedsPageContent() {
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [expandedFeedId, setExpandedFeedId] = useState<number | null>(null);
  const [error, setError] = useState<string>("");
  const [logLoading, setLogLoading] = useState(false);
  const [logError, setLogError] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const initialSearch = searchParams.get("search") || "";
  const [searchTerm, setSearchTerm] = useState<string>(initialSearch);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    const loadFeeds = async () => {
      try {
        const response = await fetch("/api/feeds");
        if (!response.ok) throw new Error("Failed to load feeds");
        const data = await response.json();
        setFeeds(data);
      } catch (err: any) {
        setError("Failed to load feeds");
        console.error(err);
      }
    };
    loadFeeds();
  }, []);

  const toggleExpand = async (feedId: number) => {
    if (expandedFeedId === feedId) {
      setExpandedFeedId(null);
      setLogError(null);
      return;
    }

    setLogLoading(true);
    setLogError(null);

    try {
      const response = await fetch(`/api/feeds/${feedId}`);
      if (!response.ok) throw new Error("Failed to fetch feed details");
      const feedData = await response.json();

      const updatedFeeds = feeds.map(f =>
        f.id === feedId ? { ...f, logs: feedData.recent_logs || [] } : f
      );
      setFeeds(updatedFeeds);
    } catch (err) {
      setLogError("FAILED to load");
    }

    setLogLoading(false);
    setExpandedFeedId(feedId);
  };

  const handleCopyLogs = (logs: FeedLog[]) => {
    const text = logs.map((log) => `${log.created_at}: ${log.message}`).join("\n");
    navigator.clipboard.writeText(text);
    alert("Logs copied to clipboard!");
  };

  const handleDownloadLogs = (logs: FeedLog[], title: string) => {
    const text = logs.map((log) => `${log.created_at}: ${log.message}`).join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${title}_logs.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredFeeds = feeds.filter(feed => feed.url.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <AdminLayout
      searchValue={searchTerm}
      onSearchChange={(e) => setSearchTerm(e.target.value)}
    >
      <AddRssFeedModal open={modalOpen} onClose={() => setModalOpen(false)} />

      {error && (
        <div className="text-red-500 font-semibold mb-4">{error}</div>
      )}

      <div className="overflow-x-auto">
        {/* Bulk Operation Buttons, Add new RSS Feed, Filtering & Sort Bar */}
        <div className="flex justify-end py-2">
          <button
            type="button"
            className="border border-black rounded-md p-1 bg-white hover:bg-gray-100 transition flex items-center justify-center"
            onClick={() => setModalOpen(true)}
            aria-label="Add New RSS Feed"
          >
            <PlusIcon className="h-5 w-5 text-black" />
          </button>
        </div>
        <FeedTable
          feeds={filteredFeeds}
          expandedFeedId={expandedFeedId}
          toggleExpand={toggleExpand}
          logLoading={logLoading}
          logError={logError}
          handleCopyLogs={handleCopyLogs}
          handleDownloadLogs={handleDownloadLogs}
        />
      </div>
    </AdminLayout>
  );
}