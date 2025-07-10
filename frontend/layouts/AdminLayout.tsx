"use client";
// layouts/AdminLayout.tsx
import React, { ReactNode} from "react";
import {useRouter} from "next/navigation";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";


type Props = {
  children: ReactNode;
  searchValue: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSearchSubmit?: () => void; 
};

export default function AdminLayout({ children, searchValue, onSearchChange, onSearchSubmit }: Props) {
  const router = useRouter();

  // Logout handler 
  const handleLogout = () => {
    router.push("/auth/logout");


  };
  return (
    <div className="flex h-screen bg-podverse-background text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <TopBar
          searchValue={searchValue}
          onSearchChange={onSearchChange}
          onSearchSubmit={onSearchSubmit}
          onLogout={handleLogout}
          onNotificationsClick={() => console.log("Notifications clicked")}
        />
        <main className="flex-1 overflow-y-auto p-2">
          {children}
        </main>
      </div>

    </div>
  );
}
