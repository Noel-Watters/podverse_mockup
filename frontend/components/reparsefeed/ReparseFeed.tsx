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
}

export default function ReparseFeed({ feedId, children }: ReparseFeedProps) {
  const dispatch = useDispatch<AppDispatch>();
  const feedState = useSelector((state: RootState) => state.reparse[feedId]);

  const handleReparse = async () => {
    dispatch(startReparse(feedId));
    try {
      await fetch(`/api/feeds/${feedId}/reparse`, { method: 'POST' });
      await dispatch(fetchFeedStatus(feedId));
    } catch (err: any) {
      // Error will be handled by Redux state
    }
  };

  return children({
    onReparse: handleReparse,
    status: feedState?.status,
    loading: feedState?.loading ?? false,
    error: feedState?.error ?? null,
  });
}