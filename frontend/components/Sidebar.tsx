"use client";
//Used on every page
import Link from "next/link";
import Image from "next/image";
import {  usePathname } from "next/navigation";
import {RssIcon } from "@heroicons/react/24/outline";
import { useDispatch } from "react-redux";
import { resetFilters } from "@/redux/feedSlice";

// Simple class name joiner utility
function cn(...classes: (string | false | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}

const navLinks = [
  { href: "/dashboard", label: "Dashboard", icon: "/Dark_Podverse_Logo.svg" },
  { href: "/rssfeed", label: "Feeds", icon: <RssIcon className="w-6 h-6" /> },




];

export default function Sidebar() {
  const pathname = usePathname();
  const dispatch = useDispatch();

   return (
    <aside className="w-20 h-auto bg-bar p-4 space-y-4">
      <nav className="flex flex-col gap-2">
        {navLinks.map(({ href, label, icon }) => (
          <Link
            key={href}
            href={href}
            onClick={href === "/rssfeed" ? () => dispatch(resetFilters()) : undefined}
          >
            <span
              className={cn(
                "px-2 py-2 rounded hover:bg-accent transition cursor-pointer flex items-center gap-2",
                pathname === href
                  ? "bg-accent text-black font-semibold "
                  : "text-black"
              )}
              title={label}
            >
              {typeof icon === "string" ? (
                <Image src={icon} alt={label} width={24} height={24} />
              ) : (
                icon
              )}
            </span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
