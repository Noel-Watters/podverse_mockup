import { FeedLog } from "@/types/feed";


export default function ChannelFeedLog({ logs }: { logs: FeedLog[] }) {
  return (
    <div className="bg-podverse-surface p-4 rounded shadow h-full">
      <h3 className="font-bold mb-2 text-black text-lg">Feed Log</h3>
      <ul className="text-sm space-y-2">
        {logs.map((log) => (
          <li key={log.id}>
            <div className="text-black">
              {log.finished_at ? new Date(log.finished_at).toLocaleString() : "N/A"}
            </div>
            <div className="text-red-400">{log.parse_error_message}</div>
            <div className="text-xs text-black">Parsed by: {log.parsed_by}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
