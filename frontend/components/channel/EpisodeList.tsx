"use client";
import {Item} from "@/types/item";
export default function EpisodeList({ items }: { items: Item[] }) {
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.id} className="bg-podverse-surface p-4 rounded shadow">
          <div className="text-lg font-semibold">{item.title}</div>
          <p className="text-sm text-gray-400">GUID: {item.guid}</p>
          <p className="text-sm text-gray-400">Published: {new Date(item.pub_date).toLocaleDateString()}</p>
          <p className="text-sm text-gray-400">Status: {item.flag_status.status}</p>
        </div>
      ))}
    </div>
  );
}
