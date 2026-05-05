import EpisodeList from "./EpisodeList";
import FeedLogTable from "../FeedLogTable";
import { Item } from "@/types/item";
import type { FeedLog } from "@/types/feed";

export default function EpisodeLogSection({ items, logs }: { items: Item[]; logs: FeedLog[] }) {
  return (
    <div className="flex flex-col md:flex-row gap-6">
      <div className="flex-1 border border-gray-300 rounded p-4 space-y-4 flex flex-col h-full">
        <h2 className="text-lg font-semibold">Episodes</h2>
        <EpisodeList items={items} />
      </div>
      <div className="w-full flex-1 border border-gray-300 rounded p-4 space-y-4 flex flex-col h-full">
        <h2 className="text-lg font-semibold">Feed Logs</h2>
        <FeedLogTable logs={logs} />
      </div>
    </div>
  );
}

