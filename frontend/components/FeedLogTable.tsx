import { FeedLog } from "@/types/feed";
import { formatDateTime } from "@/utils/formateDateTime";


export default function FeedLogTable({ logs }: { logs: FeedLog[] }) {

  return (
    <div className="flex flex-col w-full text-sm m-1 space-y-2">
      {logs.map((log) => {
        const formatted = formatDateTime(log.finished_at ?? "");
        const [date, time] = formatted.split(" ");

        return (
          <div className="flex flex-row w-full border-b border-muted min-h-[56px]" key={log.id}>
            <div className="flex flex-col flex-1 justify-center">
              <p className="font-semibold text-base">Status:{" "}
                <span className={log.parse_errors === 0 ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
                  {log.parse_errors === 0 ? "Live" : "Error"}
                </span>
              </p>
              <p className="text-muted text-xs">HTTP Status: {log.http_status ?? "N/A"}</p>
              <div className="flex pt-1 flex-row">
                <p className="font-semibold text-s">Parsed By:{" "}</p>
                <span className="text-s">{log.parsed_by ?? ""}</span>
              </div>
              <div className="flex flex-row py-1">
                <p className="font-semibold text-s">Message:{" "}</p>
                <span className="text-xs">{log.parse_error_message ?? ""}</span>
              </div>
            </div>
            <div className="flex flex-col flex-1 items-end justify-center">
              <p className="text-muted text-s">Date: <span className="font-semibold">{date}</span></p>
              <p className="text-muted text-xs"><span className="font-semibold">{time}</span></p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
