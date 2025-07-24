"use client";
import { Stats } from "@/types/stats";

export default function ChannelStats({ stats }: { stats: Stats }) {
  const statList = [
    { label: "All Time Views", value: stats.all_time_count },
    { label: "Monthly Current Views", value: stats.month_current_count },
    { label: "Weekly Current Views", value: stats.week_current_count },
    { label: "Daily Current Views", value: stats.day_1_count },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-2  h-full gap-12 p-4">
      {statList.map(({ label, value }) => (
        <div key={label} className="bg-gray-100 p-4 rounded  shadow text-left flex flex-col h-full">
          <div className="text-base text-muted font-semibold">{label}</div>
          <div className="text-3xl font-semibold">{value}</div>
        </div>
      ))}
    </div>
  );
}
