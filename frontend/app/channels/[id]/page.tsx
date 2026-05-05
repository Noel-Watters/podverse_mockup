"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ChannelLayout from "@/components/channel/ChannelLayout";
import {ChannelData} from "@/types/channel";
import ReparseNotify from "@/components/reparsefeed/ReparseNotify";

export default function ChannelPage() {
  const { id } = useParams();
  const [channelData, setChannelData] = useState<ChannelData | null>(null);
    const [notifies, setNotifies] = useState<
    {
      id: string;
      type: "success" | "error";
      message: string;
      duration?: number;
      details?: string[];
    }[]
  >([]);

  useEffect(() => {
    if (!id) return;
    const fetchChannel = async () => {
      const res = await fetch(`/api/stats/channels/${id}`);
      if (!res.ok) return;
      const json = await res.json();
      setChannelData(json.data);
    };
    fetchChannel();
  }, [id]);

  if (!channelData) return <div className="p-4 text-white">Loading…</div>;

  return (
    <>
      {/* Notifications */}
      {notifies.map((notify) => (
        <ReparseNotify
          key={notify.id}
          type={notify.type}
          message={notify.message}
          duration={notify.duration}
          details={notify.details}
          onClose={() => setNotifies(notifies.filter(n => n.id !== notify.id))}
        />
      ))}

      <ChannelLayout
        data={channelData}
        onNotify={(n) =>
          setNotifies((prev) => [
            ...prev,
            { ...n, id: crypto.randomUUID() },
          ])
        }
      />
    </>
  );
}
