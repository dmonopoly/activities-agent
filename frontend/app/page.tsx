'use client';

import ActivityChat from '@/components/chat/ActivityChat';
import Header from '@/components/ui/Header';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    let id = localStorage.getItem('userId');
    if (!id) {
      id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('userId', id);
    }
    setUserId(id);
  }, []);

  const handleHistoryChange = useCallback((newHistoryId: string) => {
    router.push(`/c/${newHistoryId}`);
  }, [router]);

  if (!userId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    );
  }

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
