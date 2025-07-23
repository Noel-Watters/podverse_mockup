"use client";
// layouts/AdminLayout.tsx
import React, { ReactNode} from "react";
import {useRouter} from "next/navigation";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import { useSelector } from "react-redux";
import { RootState } from "@/redux/store";



type Props = {
  children: ReactNode;
  searchValue: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSearchSubmit?: () => void; 
};

export default function AdminLayout({ children, searchValue, onSearchChange, onSearchSubmit }: Props) {
  const router = useRouter();
  const searchTerm = useSelector((state: RootState) => state.feeds.searchTerm);


  // Logout handler 
  const handleLogout = () => {
    router.push("/auth/logout");
  };



  return (
    <div className="flex min-h-screen text-black">
      <Sidebar />
      <div className="flex-1 flex bg-bar h-screen flex-col">
        <TopBar
          searchValue={searchValue}
          onSearchChange={onSearchChange}
          onSearchSubmit={onSearchSubmit}
          onLogout={handleLogout}
          onNotificationsClick={() => console.log("Notifications clicked")}
        />
        <main className="flex-1 overflow-auto rounded-lg border border-gray-300 bg-white shadow-lg">
          {children}
        </main>
      </div>

    </div>
  );
}
