"use client";

import { useEffect, useState } from "react";
import ActivityChat from "@/components/chat/ActivityChat";
import Header from "@/components/ui/Header";

export default function Home() {
  const [userId, setUserId] = useState<string>("");

  useEffect(() => {
    // Get user ID from localStorage (set via Preferences page)
    const id = localStorage.getItem("userId") || "";
    setUserId(id);
  }, []);

  // if (!userId) {
  //   return (
  //     <div className="min-h-screen bg-white flex flex-col">
  //       <Header />
  //       <div className="flex-1 flex items-center justify-center">
  //         <div className="text-center">
  //           <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto mb-4"></div>
  //           <p className="text-gray-600">Loading... If this persists, please <a href="/preferences" className="text-pink-600 underline">select a user profile</a>.</p>
  //         </div>
  //       </div>
  //     </div>
  //   );
  // }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header userId={userId} />

      {/* Main Chat Interface - Immersive full-height */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <ActivityChat userId={userId} />
      </main>
    </div>
  );
}
