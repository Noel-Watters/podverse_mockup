"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ChannelLayout from "@/components/channel/ChannelLayout";
import {ChannelData} from "@/types/channel";

export default function ChannelPage() {
  const { id } = useParams();
  const [channelData, setChannelData] = useState<ChannelData | null>(null);

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

  return <ChannelLayout data={channelData} />;
}
