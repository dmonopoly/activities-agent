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
    <div className="min-h-screen bg-gray-50">
      {/* Header - Airbnb-inspired */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-pink-600 hover:text-pink-700">
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

      {/* Main Chat Interface */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden" style={{ height: 'calc(100vh - 200px)', minHeight: '600px' }}>
          <ActivityChat userId={userId} />
        </div>
      </main>
    </div>
  );
}
