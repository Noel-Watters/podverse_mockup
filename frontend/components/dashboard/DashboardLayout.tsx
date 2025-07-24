"use client";
import React, { useEffect, useState } from "react";
import AdminLayout from "@/layouts/AdminLayout";
// Removed Redux imports
import { useRouter } from "next/navigation";
import DashboardHeader from "./DashboardHeaderSection";
import DashboardFeedSection from "./DashboardFeedSection";
import DashboardStatsSection from "@/components/dashboard/DashboardStatsSection";


interface DashboardLayoutProps {
  feeds: any[];
  loading: boolean;
  error: string | null;
  selectedFeedId: number | null;
  onSelectFeed: (feedId: any, logs: any) => void;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  feeds,
  loading,
  error,
  selectedFeedId,
  onSelectFeed,
}) => {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");

  const handleSearch = () => {
    setTimeout(() => {
      router.push(`/rssfeed?search=${encodeURIComponent(searchTerm)}`);
    }, 200);
  };

  return (
    <AdminLayout
      searchValue={searchTerm}
      onSearchChange={(e) => setSearchTerm(e.target.value)}
      onSearchSubmit={handleSearch}
    >
      <div className="p-6 space-y-6">
        {/* <DashboardHeader /> */}
        <DashboardFeedSection
          feeds={feeds}
          loading={loading}
          error={error}
          selectedFeedId={selectedFeedId}
          onSelectFeed={onSelectFeed}
        />
        <DashboardStatsSection />
      </div>
    </AdminLayout>
  );
};

export default DashboardLayout;