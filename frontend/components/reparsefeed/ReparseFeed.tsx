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
    let success = true;
    try {
      await dispatch(reparseFeed(feedId)).unwrap();
      await dispatch(fetchFeedStatus(feedId));
    } catch (err: any) {
      success = false;
      if (onNotify) {
        onNotify({
          type: "error",
          message: "Reparse failed: " + (err.message || "Unknown error"),
        });
      }
    }
    // delay to ensure backend has written the new log
  await new Promise(res => setTimeout(res, 1000));
  await dispatch(fetchFeedLogs(feedId));
    if (success && onNotify) {
      onNotify({
        type: "success",
        message: "Feed reparsed successfully!",
        duration: 2500,
      });
    }
  };

  return children({
    onReparse: handleReparse,
    status: feedState?.flag_status,
    loading: feedState?.reparsing ?? false,
    error: feedState?.error ?? null,
  });
}