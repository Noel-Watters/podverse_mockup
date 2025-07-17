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
import { fetchFeedLogs, bulkReparseFeeds, fetchFeedStatus } from "@/redux/reparseSlice";
import { fetchFeeds, resetFeeds, setFilters } from "@/redux/feedSlice";
import type { AppDispatch, RootState } from "@/redux/store";

export default function FeedsPageContent() {
  const [isBulkReparseLoading, setIsBulkReparseLoading] = useState(false);
  const [expandedFeedId, setExpandedFeedId] = useState<number | null>(null);
  const [selectedFeeds, setSelectedFeeds] = useState<number[]>([]);
  const searchParams = useSearchParams();
  const initialSearch = searchParams.get("search") || "";
  const [searchTerm, setSearchTerm] = useState<string>(initialSearch);
  const [modalOpen, setModalOpen] = useState(false);
  const dispatch = useDispatch<AppDispatch>();
  const { items: feeds, loading, error, offset, hasMore } = useSelector((state: RootState) => state.feeds);
  const { filters } = useSelector((state: RootState) => state.feeds);
  const scrollContainerRef = React.useRef<HTMLDivElement>(null);

  const [notifies, setNotifies] = useState<
    {
      id: string; // unique id for each toast
      type: "success" | "error";
      message: string;
      duration?: number;
      details?: string[];
    }[]
  >([]);



// Infinite scroll handler for feeds container
const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
  const target = e.currentTarget;
  if (!target) return;
  const { scrollTop, scrollHeight, clientHeight } = target;
  // If near bottom, not loading, and more feeds available, fetch next page
  if (scrollTop + clientHeight >= scrollHeight - 40 && hasMore && !loading) {
    dispatch(fetchFeeds());
  }
};


// Reset feeds and fetch first page when filters/search change
useEffect(() => {
  dispatch(resetFeeds());
  dispatch(fetchFeeds());
}, [searchTerm, filters, dispatch]);


const handleSortChange = (sort: string) => {
  dispatch(setFilters({ sort: sort as any }));
};

const handleOrderChange = (order: string) => {
  dispatch(setFilters({ order: order as any }));
};

const handleFilterChange = (filterName: string, value: string) => {
  let parsedValue: any = value;
  if (filterName === "feed_flag_status_id" || filterName === "parsing_priority") {
    parsedValue = value ? Number(value) : undefined;
  }
  if (filterName === "is_parsing") {
    if (value === "true") parsedValue = true;
    else if (value === "false") parsedValue = false;
    else parsedValue = undefined;
  }
  dispatch(setFilters({ [filterName]: parsedValue }));
};

const handleBulkReparse = async () => {
  setIsBulkReparseLoading(true);
  let failed: string[] = [];
  try {
    await dispatch(bulkReparseFeeds(selectedFeeds.map(String))).unwrap();
    await Promise.all(
      selectedFeeds.map(feedId => {
        dispatch(fetchFeedStatus(String(feedId)));
        dispatch(fetchFeedLogs(String(feedId)));
      })
    );
  } catch (err: any) {
    failed = selectedFeeds.map(feedId => `Feed ${feedId}: ${err.message || "Unknown error"}`);
  } finally {
    setNotifies(prev => [
      ...prev,
      {
        id: crypto.randomUUID(),
        type: failed.length ? "error" : "success",
        message: failed.length
          ? `Bulk reparse completed with errors.`
          : `Bulk reparse completed successfully for ${selectedFeeds.length} feeds.`,
        details: failed.length ? failed : undefined,
        duration: failed.length ? undefined : 2500,
      },
    ]);
    setIsBulkReparseLoading(false);
  }
};

const handleBulkUpdateStatus = async (newStatus: string) => {
  await fetch("/api/feeds/bulk-update-status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feed_ids: selectedFeeds, new_status: newStatus }),
  });
};


const toggleExpand = (feedId: number) => {
  if (expandedFeedId === feedId) {
    setExpandedFeedId(null);
    return;
  }
  dispatch(fetchFeedLogs(String(feedId))); // Make sure to use String(feedId) if your state uses string keys
  setExpandedFeedId(feedId);
};



  // Filtering is done client-side after all loaded feeds
  const filteredFeeds = feeds.filter(feed => feed.url.toLowerCase().includes(searchTerm.toLowerCase()));



  return (
    <AdminLayout
      searchValue={searchTerm}
      onSearchChange={(e) => setSearchTerm(e.target.value)}
    >
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="overflow-y-auto h-[80vh] p-4"
        style={{ position: "relative" }}
      >
        {/* Notifications */}
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

        {/* Toolbar for bulk actions, add, sort, filter */}
        <FeedToolBar
          onSortChange={handleSortChange}
          onOrderChange={handleOrderChange}
          onFilterChange={handleFilterChange}
          selectedFeeds={selectedFeeds}
          onBulkReparse={handleBulkReparse}
          onBulkUpdateStatus={handleBulkUpdateStatus}
          isBulkReparseLoading={isBulkReparseLoading}
        />
        <FeedTable
          feeds={filteredFeeds}
          expandedFeedId={expandedFeedId}
          toggleExpand={toggleExpand}
          onNotify={(n) =>
            setNotifies((prev) => [
              ...prev,
              { ...n, id: crypto.randomUUID() },
            ])
          }
          selectedFeeds={selectedFeeds}
          setSelectedFeeds={setSelectedFeeds}
        />

        {/* Infinite scroll loader indicator */}
        {loading && (
          <div className="text-center py-4 text-podverse-muted">Loading more feeds...</div>
        )}
        {!hasMore && (
          <div className="text-center py-4 text-podverse-muted">No more feeds to load.</div>
        )}
      </div>
    </AdminLayout>
  );
}