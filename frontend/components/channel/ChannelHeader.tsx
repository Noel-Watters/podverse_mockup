"use client";
import { CalendarIcon, RssIcon } from "@heroicons/react/24/outline";
import { ChannelData } from "@/types/channel";

export default function ChannelHeader({ data }: { data: ChannelData }) {
  return (
    <div className="bg-podverse-surface p-6 rounded-xl shadow space-y-2">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-black">{data.title}</h1>
          <p className="text-sm text-black">Podcast Index ID: {data.podcast_index_id}</p>
          <p className="text-sm text-black">Status: {data.feed.flag_status}</p>
        </div>
        <button className="bg-podverse-accent text-white px-4 py-1 rounded-md">Reparse</button>
      </div>

      <div className="flex flex-wrap gap-2">
        {data.categories.map((id) => (
          <span key={id} className="text-xs bg-gray-300 px-2 py-1 rounded-full">
            Category #{id}
          </span>
        ))}
        <span className="text-xs bg-gray-300 px-2 py-1 rounded-full">Medium ID: {data.medium_id}</span>
        <a href={data.feed.url} className="flex items-center text-blue-300 border px-2 py-1 rounded border-blue-400 text-xs">
          <RssIcon className="h-4 w-4 mr-1" />
          RSS
        </a>
        <span className="text-xs border px-2 py-1 rounded border-gray-500 text-gray-400 flex items-center">
          <CalendarIcon className="h-4 w-4 mr-1" />
          Launched: {data.feed.created_at ? new Date(data.feed.created_at).toLocaleDateString() : "-"}
        </span>
      </div>
    </div>
  );
}
