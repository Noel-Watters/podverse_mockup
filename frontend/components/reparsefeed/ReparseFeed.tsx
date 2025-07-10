"use client";
import { useDispatch, useSelector } from 'react-redux';
import { startReparse, fetchFeedStatus } from '../../redux/reparseSlice';
import type { AppDispatch, RootState } from '../../redux/store';

interface ReparseFeedProps {
  feedId: string;
  children: (props: {
    onReparse: () => void;
    status: string | undefined;
    loading: boolean;
    error: string | null;
  }) => React.ReactNode;
    onNotify?: (n: {
    type: "success" | "error";
    message: string;
    duration?: number;
    details?: string[];
  }) => void;
}

export default function ReparseFeed({ feedId, children, onNotify }: ReparseFeedProps) {
  const dispatch = useDispatch<AppDispatch>();
  const feedState = useSelector((state: RootState) => state.reparse[feedId]);

  const handleReparse = async () => {
    dispatch(startReparse(feedId));
    try {
      const response = await fetch(`/api/feeds/${feedId}/reparse`, { method: 'POST' });
      await dispatch(fetchFeedStatus(feedId));
    if (!response.ok) {
      // Try to extract error message from response body if available
      let errorMsg = `HTTP ${response.status}`;
      try {
        const data = await response.json();
        if (data && data.error) errorMsg = data.error;
      } catch {}
      throw new Error(errorMsg);
    }
    await dispatch(fetchFeedStatus(feedId));
    if (onNotify) {
      onNotify({
        type: "success",
        message: "Feed reparsed successfully!",
        duration: 2500,
      });
    }
  } catch (err: any) {
    if (onNotify) {
      onNotify({
        type: "error",
        message: "Reparse failed: " + (err.message || "Unknown error"),
      });
    }
  }
};
  

  return children({
    onReparse: handleReparse,
    status: feedState?.status,
    loading: feedState?.loading ?? false,
    error: feedState?.error ?? null,
  });
}