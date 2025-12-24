'use client';

import ActivityChat from '@/components/chat/ActivityChat';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const chatId = params.id as string;
  
  const [userId, setUserId] = useState<string>('');
  const [initialMessages, setInitialMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    let id = localStorage.getItem('userId');
    if (!id) {
      id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('userId', id);
    }
    setUserId(id);

    loadChatHistory();
  }, [chatId]);

  const loadChatHistory = async () => {
    try {
      const history = await api.getChatHistory(chatId);
      setInitialMessages(history.messages as Message[]);
    } catch (error) {
      console.error('Failed to load chat history:', error);
      setNotFound(true);
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryChange = useCallback((newHistoryId: string) => {
    if (newHistoryId !== chatId) {
      router.push(`/c/${newHistoryId}`);
    }
  }, [chatId, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    );
  }

  if (notFound) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <Link href="/" className="text-2xl font-bold text-[#FF385D]">
                Activities Agent
              </Link>
              <nav className="flex gap-6">
                <Link href="/" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                  New Chat
                </Link>
                <Link href="/history" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                  Chat History
                </Link>
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
        <main className="flex-1 flex flex-col items-center justify-center">
          <div className="text-center">
            <div className="text-gray-400 text-6xl mb-4">🔍</div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">Chat not found</h1>
            <p className="text-gray-600 mb-6">This conversation may have been deleted.</p>
            <Link
              href="/"
              className="inline-flex items-center px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-colors"
            >
              Start a new chat
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-[#FF385D]">
              Activities Agent
            </Link>
            <nav className="flex gap-6">
              <Link href="/" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                New Chat
              </Link>
              <Link href="/history" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Chat History
              </Link>
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

      <main className="flex-1 flex flex-col overflow-hidden">
        <ActivityChat 
          userId={userId} 
          historyId={chatId}
          initialMessages={initialMessages}
          onHistoryChange={handleHistoryChange}
        />
      </main>
    </div>
  );
}

