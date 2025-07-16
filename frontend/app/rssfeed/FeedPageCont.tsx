"use client";
import React, { useState, useEffect } from "react";
import { Feed, FeedLog } from "@/types/feed";
import AdminLayout from "@/layouts/AdminLayout";
import { useSearchParams } from "next/navigation";
import AddRssFeedModal from "@/components/AddRssFeedModal";
import FeedTable from "@/components/rssfeed/FeedTable";
import ReparseNotify from "@/components/reparsefeed/ReparseNotify";
import FeedToolBar from "@/components/rssfeed/FeedToolbar";
import { useDispatch, useSelector } from "react-redux";
import { fetchFeedLogs } from "@/redux/reparseSlice";
import { fetchFeeds, resetFeeds } from "@/redux/feedSlice";
import type { AppDispatch, RootState } from "@/redux/store";

export default function FeedsPageContent() {
  //const [feeds, setFeeds] = useState<Feed[]>([]);
  const [expandedFeedId, setExpandedFeedId] = useState<number | null>(null);
  //const [error, setError] = useState<string>("");
  const searchParams = useSearchParams();
  const initialSearch = searchParams.get("search") || "";
  const [searchTerm, setSearchTerm] = useState<string>(initialSearch);
  const [modalOpen, setModalOpen] = useState(false);
  const dispatch = useDispatch<AppDispatch>();
  const { items: feeds, loading, error, offset, hasMore } = useSelector((state: RootState) => state.feeds);

  const [notifies, setNotifies] = useState<
    {
      id: string; // unique id for each toast
      type: "success" | "error";
      message: string;
      duration?: number;
      details?: string[];
    }[]
  >([]);


const scrollRef = React.useRef<HTMLDivElement>(null);
useEffect(() => {
  const scrollContainer = scrollRef.current;
  if (!scrollContainer) return;
  const onScroll = () => {
    if (
      scrollContainer.scrollHeight - scrollContainer.scrollTop <= scrollContainer.clientHeight + 50 &&
      hasMore &&
      !loading
    ) {
      dispatch(fetchFeeds(offset));
    }
  };
  scrollContainer.addEventListener("scroll", onScroll);
  return () => scrollContainer.removeEventListener("scroll", onScroll);
}, [dispatch, offset, hasMore, loading]);

useEffect(() => {
  dispatch(resetFeeds());
  dispatch(fetchFeeds(0));
}, [searchTerm, dispatch]);





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

      <div ref={scrollRef} className="overflow-y-auto h-[600px]">
        {/* Toolbar for bulk actions, add, sort, filter */}
        <FeedToolBar  />
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