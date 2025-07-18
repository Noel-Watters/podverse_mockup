"use client";
import React from 'react';
import FeedStatsChart from "@/components/FeedStatsChart";
export default function DashboardStatsSection() {
  // Placeholder values, replace with real data or props as needed
  const totalFeeds = 1200;
  const healthyFeeds = 1050;
  const flaggedFeeds = 150;
  const flaggedPercent = ((flaggedFeeds / totalFeeds) * 100).toFixed(1);



  return (
    <>
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="border rounded p-4 space-y-4">
          <div className="flex items-center mb-4">
            <h2 className="text-lg font-semibold">Podverse Feed Stats</h2>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm text-left">
            <div className="bg-white rounded p-4 flex flex-col justify-between border border-gray-400">
              <p className="text-gray-500">Total RSS Feeds</p>
              <h3 className="text-2xl font-semibold text-black">{totalFeeds.toLocaleString()}</h3>
            </div>
            <div className="bg-white rounded p-4 flex flex-col justify-between border border-gray-400">
              <p className="text-gray-500">Healthy Feeds</p>
              <h3 className="text-2xl font-semibold text-black">{healthyFeeds.toLocaleString()}</h3>
            </div>
            <div className="bg-white rounded p-4 flex flex-col justify-between border border-gray-400">
              <p className="text-gray-500">Flagged Feeds</p>
              <h3 className="text-2xl font-semibold text-black">{flaggedFeeds.toLocaleString()}</h3>
            </div>
            <div className="bg-white rounded p-4 flex flex-col justify-between border border-gray-400">
              <p className="text-gray-500">Flagged %</p>
              <h3 className="text-2xl font-semibold text-black">{flaggedPercent}%</h3>
            </div>
          </div>
        </div>

        <div className="border rounded p-4">
          <h2 className="text-lg font-semibold mb-4">Healthy vs Flagged Feeds</h2>
          <FeedStatsChart healthy={healthyFeeds} flagged={flaggedFeeds} />
        </div>
      </section>

    </>
  );
}
