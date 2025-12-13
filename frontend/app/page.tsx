'use client';

import ActivityChat from '@/components/chat/ActivityChat';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Home() {
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    // Generate or retrieve user ID (in production, use proper auth)
    let id = localStorage.getItem('userId');
    if (!id) {
      id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('userId', id);
    }
    setUserId(id);
  }, []);

  if (!userId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header - Clean and minimal */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-[#FF385D]">
              Activities Agent
            </Link>
            <nav className="flex gap-6">
              <Link href="/activities" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Browse Activities
              </Link>
              <Link href="/preferences" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Preferences
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Chat Interface - Immersive full-height */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <ActivityChat userId={userId} />
      </main>
    </div>
  );
}
