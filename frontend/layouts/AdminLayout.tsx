// layouts/AdminLayout.tsx
import { ReactNode, useState} from "react";
import {useRouter} from "next/navigation";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";


type Props = {
  children: ReactNode;
};

export default function AdminLayout({ children }: Props) {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState<string>("");

  // Logout handler 
  const handleLogout = () => {
    router.push("/auth/logout");
  };
  return (
    <div className="flex h-screen bg-podverse-background text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <TopBar
          searchValue={searchTerm}
          onSearchChange={(e) => setSearchTerm(e.target.value)}
          onLogout={handleLogout}
          onNotificationsClick={() => console.log("Notifications clicked")}
        />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>

    </div>
  );
}
