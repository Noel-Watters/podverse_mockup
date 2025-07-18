import EpisodeList from "./EpisodeList";
import FeedLogTable from "../FeedLogTable";
import { Item } from "@/types/item";
import type { FeedLog } from "@/types/feed";

export default function EpisodeLogSection({ items, logs }: { items: Item[]; logs: FeedLog[] }) {
  return (
    <div className="flex flex-col md:flex-row gap-6">
      <div className="flex-1">
        <h2 className="text-lg font-semibold mb-4">Episodes</h2>
        <EpisodeList items={items} />
      </div>
      <div className="w-full flex-1">
        <h2 className="text-lg font-semibold mb-4">Feed Logs</h2>
        <FeedLogTable logs={logs} />
      </div>
    </div>
  );
}

