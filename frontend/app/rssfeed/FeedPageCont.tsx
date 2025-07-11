"use client";
import React, { useState, useEffect } from "react";
import { Feed, FeedLog } from "@/types/feed";
import AdminLayout from "@/layouts/AdminLayout";
import { useSearchParams } from "next/navigation";
import AddRssFeedModal from "@/components/AddRssFeedModal";
import FeedTable from "@/components/rssfeed/FeedTable";
import ReparseNotify from "@/components/reparsefeed/ReparseNotify";
import FeedToolBar from "@/components/rssfeed/FeedToolbar";
import { useDispatch } from "react-redux";
import { fetchFeedLogs } from "@/redux/reparseSlice";
import type { AppDispatch } from "@/redux/store";

export default function FeedsPageContent() {
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [expandedFeedId, setExpandedFeedId] = useState<number | null>(null);
  const [error, setError] = useState<string>("");
  const searchParams = useSearchParams();
  const initialSearch = searchParams.get("search") || "";
  const [searchTerm, setSearchTerm] = useState<string>(initialSearch);
  const [modalOpen, setModalOpen] = useState(false);

  const [notifies, setNotifies] = useState<
    {
      id: string; // unique id for each toast
      type: "success" | "error";
      message: string;
      duration?: number;
      details?: string[];
    }[]
  >([]);

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

const dispatch = useDispatch<AppDispatch>();

const toggleExpand = (feedId: number) => {
  if (expandedFeedId === feedId) {
    setExpandedFeedId(null);
    return;
  }
  dispatch(fetchFeedLogs(String(feedId))); // Make sure to use String(feedId) if your state uses string keys
  setExpandedFeedId(feedId);
};

  const handleCopyLogs = (logs: FeedLog[]) => {
    const text = logs.map((log) => `${log.started_at ?? ""}: ${log.parse_error_message ?? ""}`).join("\n");
    navigator.clipboard.writeText(text);
    alert("Logs copied to clipboard!");
  };

  const handleDownloadLogs = (logs: FeedLog[], title: string) => {
    const text = logs.map((log) => `${log.started_at ?? ""}: ${log.parse_error_message ?? ""}`).join("\n");
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
      {notifies.map((notify) => (
        <ReparseNotify
          key={notify.id}
          type={notify.type}
          message={notify.message}
          duration={notify.duration}
          details={notify.details}
          onClose={() => setNotifies(notifies.filter(n => n.id !== notify.id))}
        />
      ))}

      <AddRssFeedModal open={modalOpen} onClose={() => setModalOpen(false)} />

      {error && (
        <div className="text-red-500 font-semibold mb-4">{error}</div>
      )}

      <div className="overflow-x-auto">
        {/* Toolbar for bulk actions, add, sort, filter */}
        <FeedToolBar onAddFeed={() => setModalOpen(true)} />
        <FeedTable
          feeds={filteredFeeds}
          expandedFeedId={expandedFeedId}
          toggleExpand={toggleExpand}
          handleCopyLogs={handleCopyLogs}
          handleDownloadLogs={handleDownloadLogs}
          onNotify={(n) =>
            setNotifies((prev) => [
              ...prev,
              { ...n, id: crypto.randomUUID() },
            ])
          }
        />
      </div>
    </AdminLayout>
  );
}