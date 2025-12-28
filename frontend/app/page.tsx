"use client";

import ActivityChat from '@/components/chat/ActivityChat';
import Header from '@/components/ui/Header';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    const id = localStorage.getItem('userId') || '';
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

      <main className="flex-1 flex flex-col overflow-hidden">
        <ActivityChat 
          userId={userId} 
          onHistoryChange={handleHistoryChange}
        />
      </main>
    </div>
  );
}
