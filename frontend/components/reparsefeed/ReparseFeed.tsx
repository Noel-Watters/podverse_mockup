"use client";
import { useDispatch, useSelector } from 'react-redux';
import { startReparse, fetchFeedStatus, fetchFeedLogs, reparseFeed } from '../../redux/reparseSlice';
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
      await dispatch(reparseFeed(feedId)).unwrap();
      await dispatch(fetchFeedStatus(feedId));
      await dispatch(fetchFeedLogs(feedId));
      const latestFeedStatus = (await dispatch(fetchFeedStatus(feedId))).payload;
      // Type guard: check if payload is object and has status
      if (
        latestFeedStatus &&
        typeof latestFeedStatus === 'object' &&
        'status' in latestFeedStatus &&
        (latestFeedStatus as { status?: string }).status === 'error'
      ) {
        if (onNotify) {
          onNotify({
            type: "error",
            message: "Reparse failed: Feed status is error.",
          });
        }
        return;
      }
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
    loading: feedState?.reparsing ?? false,
    error: feedState?.error ?? null,
  });
}