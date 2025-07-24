import React from "react";

interface Log {
  finished_at: string; // ISO date string
}

interface HealthDurationProps {
  recent_logs: Log[];
}

function getRelevantDuration(finishedAt: string): string {
  const finishedDate = new Date(finishedAt);
  const now = new Date();
  // Clamp diffMs to zero if finished_at is in the future
  const diffMs = Math.max(0, now.getTime() - finishedDate.getTime());
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  const diffMonths = Math.floor(diffMs / (30 * 86400000));

  if (diffMins < 1) {
    return '< 1 min';
  } else if (diffMins < 60) {
    return `${diffMins} min${diffMins !== 1 ? 's' : ''}`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''}`;
  } else if (diffDays < 30) {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''}`;
  } else {
    return `${diffMonths} month${diffMonths !== 1 ? 's' : ''}`;
  }
}

const HealthDuration: React.FC<HealthDurationProps> = ({ recent_logs }) => {
  if (!recent_logs || recent_logs.length === 0) return <span>-</span>;
  // Find the most recent log (assume sorted, else sort by finished_at desc)
  const sortedLogs = [...recent_logs].sort((a, b) => new Date(b.finished_at).getTime() - new Date(a.finished_at).getTime());
  const mostRecent = sortedLogs[0];
  if (!mostRecent.finished_at) return <span>-</span>;
  const duration = getRelevantDuration(mostRecent.finished_at);
  return (
    <div className= "flex flex-col items-center border border-gray-400 rounded h-11 w-24">
        <p className="text-xs text-muted">Duration</p>
        <span className="font-semibold text-base"title={`Since ${new Date(mostRecent.finished_at).toLocaleString()}`}>{duration}</span>
    </div>
  );
};

export default HealthDuration;
