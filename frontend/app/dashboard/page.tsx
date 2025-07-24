"use client";
import React, { useEffect, useState } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import ReparseNotify from "@/components/reparsefeed/ReparseNotify";
import { useDispatch, useSelector } from "react-redux";
import { fetchFeeds, resetFeeds, setFilters } from "@/redux/feedSlice";
import { RootState, AppDispatch } from "@/redux/store";
import { fetchChannelsByFeedIds } from "@/redux/batchChannelSlice";

export default function Page() {
  const dispatch = useDispatch<AppDispatch>();
  const feeds = useSelector((state: RootState) => state.feeds.items);
  const loading = useSelector((state: RootState) => state.feeds.loading);
  const error = useSelector((state: RootState) => state.feeds.error);
  const channelsByFeedId = useSelector((state: RootState) => state.batchChannel.data);
  const [selectedFeedId, setSelectedFeedId] = useState<number | null>(null);
  const [selectedFeedLogs, setSelectedFeedLogs] = useState<any[]>([]);
  const [notifies, setNotifies] = useState<
  {
    id: string;
    type: "success" | "error";
    message: string;
    duration?: number;
    details?: string[];
  }[]
>([]);

  // Preset filters for flagged feeds
  useEffect(() => {
    dispatch(setFilters({
      status: "parse_error",
      sort_by: "updated_at",
      sort_order: "desc",
      limit: 20,
      page: 1,
    }));
    dispatch(resetFeeds());
    dispatch(fetchFeeds());
  }, [dispatch]);

    useEffect(() => {
      if (feeds.length > 0) {
        dispatch(fetchChannelsByFeedIds(feeds.map(f => f.id)));
      }
    }, [feeds, dispatch]);

  return (
    <>
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
      <DashboardLayout
        feeds={feeds}
        loading={loading}
        error={error ?? null}
        selectedFeedId={selectedFeedId}
        onSelectFeed={(feedId, logs) => {
          setSelectedFeedId(feedId);
          setSelectedFeedLogs(logs);
        }}
        onNotify={(n) =>
          setNotifies((prev) => [
            ...prev,
            { ...n, id: crypto.randomUUID() },
          ])
        }
      />
    </>
  );
}
