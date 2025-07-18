import EpisodeList from "./EpisodeList";
import ChannelFeedLog from "./ChannelFeedLog";
import { Item } from "@/types/item";
import type { FeedLog } from "@/types/feed";

export default function EpisodeLogSection({ items, logs }: { items: Item[]; logs: FeedLog[] }) {
  return (
    <div className="flex flex-col md:flex-row gap-6">
      <div className="flex-1">
        <EpisodeList items={items} />
      </div>
      <div className="w-full md:w-1/4">
        <ChannelFeedLog logs={logs} />
      </div>
    </div>
  );
}

