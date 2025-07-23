import React from "react";

interface Log {
  parse_errors: number;
  finished_at: string;
}

interface HealthBadgeProps {
  recent_logs: Log[];
}

const Healthbadge: React.FC<HealthBadgeProps> = ({ recent_logs }) => {
  if (!recent_logs || recent_logs.length === 0) return <span>-</span>;
  // Find the most recent log (assume sorted, else sort by finished_at desc)
  const sortedLogs = [...recent_logs].sort((a, b) => new Date(b.finished_at).getTime() - new Date(a.finished_at).getTime());
  const mostRecent = sortedLogs[0];
  const isLive = mostRecent.parse_errors === 0;
  const badgeText = isLive ? "Live" : "Error";
  const badgeClass = isLive
    ? "bg-gradient-to-r from-[#70F57D] to-[#0BC01D] text-gray-700 border border-gray-500 shadow-md rounded-full  w-32 py-1.5 font-bold"
    : "bg-gradient-to-r from-[#D42121] to-[#720808] text-gray-200 border border-gray-500 shadow-md rounded-full w-32 py-1.5 font-bold";
  return (
        <span className={badgeClass} style={{ minWidth: "70px", display: "inline-block", textAlign: "center" }}>
            {badgeText}
        </span>
  );
};

export default Healthbadge;
