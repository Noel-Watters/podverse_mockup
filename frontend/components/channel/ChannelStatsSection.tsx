"use client";
import React from 'react';
import ChannelStats from "./ChannelStats";
import ChannelStatsCharts from "./ChannelStatsChats";
import { Stats } from "@/types/stats";

export default function ChannelStatsSection({ stats }: { stats: Stats }) {

  return (
    <>
      <div className="flex flex-row h-[400px] gap-12 p-4">
        <div className="flex-1 border border-gray-300 rounded p-4 space-y-4 flex flex-col h-full">
          <ChannelStats stats={stats} />
        </div>

        <div className="flex-1 border border-gray-300 rounded p-4 flex flex-col h-full">
           <ChannelStatsCharts stats={stats} /> 
        </div>
      </div>

    </>
  );
}