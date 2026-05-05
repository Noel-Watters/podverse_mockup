"use client";
import React, { Suspense } from 'react';
import FeedsPageContent from './FeedPageCont';

export default function FeedsPage() {
  return (
    <Suspense fallback={<div>Loading feeds...</div>}>
      <FeedsPageContent />
    </Suspense>
  );
}