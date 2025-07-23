"use client";
import { Item } from "@/types/item";
import { LinkIcon, CalendarDaysIcon } from "@heroicons/react/24/outline";
import { FEED_STATUS_MAP } from "@/types/feed";

export default function EpisodeList({ items }: { items: Item[] }) {
  return (
    <div className="space-y-4">
      {items.map((item, idx) => (
        <div key={item.id} className="bg-podverse-surface p-4 rounded shadow flex flex-row items-stretch min-h-[96px]">
          <div className="flex items-center justify-top pr-4">
            <span className="text-5xl font-extrabold text-gray-600 leading-none select-none">{idx + 1}. </span>
          </div>
          <div className="flex-1 flex flex-col justify-between">
            <div className="flex flex-row justify-between items-start w-full">
              <div className="text-lg font-semibold">{item.title}</div>
              <div className="flex items-center space-x-1">
                <CalendarDaysIcon className="h-4 w-4" />
                <span className="text-sm">{new Date(item.pub_date).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="flex flex-row items-center space-x-2 mt-2">
              <span className="text-xs flex border px-2 py-1 rounded border-gray-400 items-center overflow-x-auto whitespace-nowrap max-w-full">
                <LinkIcon className="h-4 w-4 mr-1 text-gray-400" />
                <span className="whitespace-nowrap">{item.guid}</span>
              </span>
              <span className={`text-xs px-2 py-1 rounded font-semibold border ${FEED_STATUS_MAP[item.flag_status.status]?.className || 'border-gray-400 text-gray-500'}`}>
                {FEED_STATUS_MAP[item.flag_status.status]?.label || item.flag_status.status}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
