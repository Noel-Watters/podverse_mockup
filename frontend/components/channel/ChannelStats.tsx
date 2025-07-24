"use client";
import { Stats } from "@/types/stats";

export default function ChannelStats({ stats }: { stats: Stats }) {
  const statList = [
    { label: "All Time", value: stats.all_time_count },
    { label: "Month Current", value: stats.month_current_count },
    { label: "Week Current", value: stats.week_current_count },
    { label: "Day Current", value: stats.day_1_count },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {statList.map(({ label, value }) => (
        <div key={label} className="bg-podverse-surface p-4 rounded shadow text-center">
          <div className="text-sm text-gray-400">{label}</div>
          <div className="text-xl font-semibold">{value}</div>
        </div>
      ))}
    </div>
  );
}
