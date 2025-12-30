"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import ActivityChat from "@/components/chat/ActivityChat";
import Header from "@/components/ui/Header";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const chatId = params.id as string;

  const [userId, setUserId] = useState<string>("");
  const [initialMessages, setInitialMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    let id = localStorage.getItem("userId");
    if (!id) {
      id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("userId", id);
    }
    setUserId(id);

    loadChatHistory();
  }, [chatId]);

  const loadChatHistory = async () => {
    try {
      const history = await api.getChatHistory(chatId);
      setInitialMessages(history.messages as Message[]);
    } catch (error) {
      console.error("Failed to load chat history:", error);
      setNotFound(true);
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryChange = useCallback(
    (newHistoryId: string) => {
      if (newHistoryId !== chatId) {
        router.push(`/c/${newHistoryId}`);
      }
    },
    [chatId, router]
  );

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white transition-colors dark:bg-gray-900">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-rose-600"></div>
      </div>
    );
  }

  if (notFound) {
    return (
      <div className="flex min-h-screen flex-col bg-white transition-colors dark:bg-gray-900">
        <Header userId={userId} />
        <main className="flex flex-1 flex-col items-center justify-center">
          <div className="text-center">
            <div className="mb-4 text-6xl text-gray-400">🔍</div>
            <h1 className="mb-2 text-2xl font-semibold text-gray-900 dark:text-white">
              Chat not found
            </h1>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              This conversation may have been deleted.
            </p>
            <Link
              href="/"
              className="inline-flex items-center rounded-lg bg-rose-500 px-4 py-2 text-white transition-colors hover:bg-rose-600"
            >
              Start a new chat
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-white transition-colors dark:bg-gray-900">
      <Header userId={userId} />

      <main className="flex flex-1 flex-col overflow-hidden">
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
