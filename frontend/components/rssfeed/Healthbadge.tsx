import React from "react";

interface Log {
  parse_errors: number;
  finished_at: string;
}

interface HealthBadgeProps {
  recent_logs: Log[];
  reparsing?: boolean;
  flag_status?: string;
}

const statusMap: Record<number, { text: string; className: string }> = {
  0: { text: "Live", className: "bg-gradient-to-r from-[#70F57D] to-[#0BC01D] text-gray-700" },
  1: { text: "Error", className: "bg-gradient-to-r from-[#D42121] to-[#720808] text-gray-200" },
  2: { text: "Flagged", className: "bg-gradient-to-r from-yellow-400 to-yellow-700 text-gray-200" },
  3: { text: "Pending", className: "bg-gradient-to-r from-blue-300 to-blue-500 text-gray-800" },
  4: { text: "Archived", className: "bg-gradient-to-r from-gray-400 to-gray-700 text-gray-200" },
};

const Healthbadge: React.FC<HealthBadgeProps> = ({ recent_logs, reparsing, flag_status }) => {

  const sortedLogs = [...recent_logs].sort((a, b) => new Date(b.finished_at).getTime() - new Date(a.finished_at).getTime());
  const mostRecent = sortedLogs[0];
  console.log(flag_status)

  let status = 0; // Default status
  if (reparsing) {
    status = 3; // Reparsing
  }
  else if (flag_status ==="archived") {
    status = 4; // Archived
  }
   else if (["spam", "takedown", "pending-archive"].includes(flag_status ?? "")) {
    status = 2; // Flagged
  }
  else if (mostRecent.parse_errors === 0) {
    status = 0; // Live
  }
  else if (mostRecent.parse_errors > 0) {
    status = 1; // Error
  }
  else {
      return <span>-</span>;
  }

const { text, className } = statusMap[status];

  return (
    <span
      className={`border border-gray-500 shadow-md rounded-full w-32 py-1.5 font-bold text-center inline-block ${className}`}
    >
      {text}
    </span>
  );
};

export default Healthbadge;
