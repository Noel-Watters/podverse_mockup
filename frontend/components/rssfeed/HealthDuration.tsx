import React, {useEffect, useState} from "react";
import { parseNaiveAsUTC } from "@/utils/datetime";
import { DateTime } from "luxon";

interface Log {
  finished_at: string; // ISO date string
}

interface HealthDurationProps {
  recent_logs: Log[];
}

function getRelevantDuration(finishedAt: string): string {
  const finished = parseNaiveAsUTC(finishedAt);
  const now = DateTime.utc();
  const diff = now.diff(finished, ["months", "days", "hours", "minutes"]).toObject();

  if ((diff.minutes ?? 0) < 1) {
    return "< 1 min";
  } else if ((diff.minutes ?? 0) < 60) {
    return `${Math.floor(diff.minutes!)} min${Math.floor(diff.minutes!) !== 1 ? "s" : ""}`;
  } else if ((diff.hours ?? 0) < 24) {
    return `${Math.floor(diff.hours!)} hour${Math.floor(diff.hours!) !== 1 ? "s" : ""}`;
  } else if ((diff.days ?? 0) < 30) {
    return `${Math.floor(diff.days!)} day${Math.floor(diff.days!) !== 1 ? "s" : ""}`;
  } else {
    return `${Math.floor(diff.months!)} month${Math.floor(diff.months!) !== 1 ? "s" : ""}`;
  }
}

const HealthDuration: React.FC<HealthDurationProps> = ({ recent_logs }) => {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTick(t => t + 1);
    }, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);


  if (!recent_logs || recent_logs.length === 0) return <span>-</span>;
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
