// frontend/app/not-found.tsx
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function NotFoundPage() {
  const router = useRouter();
  const [seconds, setSeconds] = useState(5);

  useEffect(() => {
    if (seconds === 0) {
      router.push("/dashboard");
    }
    const timer = setTimeout(() => setSeconds(s => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [seconds, router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className="text-4xl font-bold mb-4">404 page not found</div>
      {/* Spinner here */}
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-500 border-solid mb-4"></div>
      <div className="text-lg text-gray-500">
        Redirecting to dashboard in {seconds}...
      </div>
    </div>
  );
}