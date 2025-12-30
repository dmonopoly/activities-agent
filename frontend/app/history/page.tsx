"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import Header from "@/components/ui/Header";
import { api, ChatHistoryListItem } from "@/lib/api";

export default function HistoryPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string>("");
  const [histories, setHistories] = useState<ChatHistoryListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    let id = localStorage.getItem("userId");
    if (!id) {
      id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("userId", id);
    }
    setUserId(id);
  }, []);

  useEffect(() => {
    loadHistories();
  }, []);

  const loadHistories = async () => {
    try {
      setLoading(true);
      const data = await api.getChatHistories();
      setHistories(data);
    } catch (error) {
      console.error("Error loading chat histories:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoad = (historyId: string) => {
    router.push(`/c/${historyId}`);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmId) return;

    try {
      setDeletingId(deleteConfirmId);
      await api.deleteChatHistory(deleteConfirmId);
      setHistories((prev) => prev.filter((h) => h.id !== deleteConfirmId));
      setDeleteConfirmId(null);
    } catch (error) {
      console.error("Error deleting chat history:", error);
      alert("Failed to delete chat history. Please try again.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearAll = async () => {
    try {
      await api.clearAllChatHistory();
      setHistories([]);
      setShowClearConfirm(false);
    } catch (error) {
      console.error("Error clearing chat histories:", error);
      alert("Failed to clear chat histories. Please try again.");
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="flex min-h-screen flex-col bg-white transition-colors dark:bg-gray-900">
      <Header userId={userId} />

      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
              Chat History
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              View and manage your saved conversations.
            </p>
          </div>
          {histories.length > 0 && (
            <button
              onClick={() => setShowClearConfirm(true)}
              className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-600 transition-colors hover:bg-red-100 dark:border-red-800 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50"
            >
              Clear All History
            </button>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-rose-600"></div>
          </div>
        ) : histories.length === 0 ? (
          <div className="py-12 text-center">
            <div className="mb-4 text-6xl text-gray-400">💬</div>
            <p className="mb-4 text-lg text-gray-500 dark:text-gray-400">
              No chat history yet.
            </p>
            <Link
              href="/"
              className="inline-flex items-center rounded-lg bg-rose-500 px-4 py-2 text-white transition-colors hover:bg-rose-600"
            >
              Start a new conversation
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {histories.map((history) => (
              <div
                key={history.id}
                className="rounded-xl border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <h3 className="truncate font-medium text-gray-900 dark:text-white">
                      {history.title}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(history.updated_at)} · {history.message_count}{" "}
                      messages
                    </p>
                  </div>
                  <div className="flex flex-shrink-0 gap-2">
                    <button
                      onClick={() => handleLoad(history.id)}
                      className="rounded-lg bg-rose-500 px-3 py-1.5 text-sm text-white transition-colors hover:bg-rose-600"
                    >
                      Load
                    </button>
                    <button
                      onClick={() => setDeleteConfirmId(history.id)}
                      disabled={deletingId === history.id}
                      className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-200 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
                    >
                      {deletingId === history.id ? "Deleting..." : "Delete"}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Clear All Confirmation Modal */}
      {showClearConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="mx-4 max-w-md rounded-xl bg-white p-6 shadow-xl dark:bg-gray-800">
            <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
              Clear All History?
            </h3>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              This will permanently delete all your chat history. This action
              cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowClearConfirm(false)}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleClearAll}
                className="rounded-lg bg-red-500 px-4 py-2 text-sm text-white transition-colors hover:bg-red-600"
              >
                Clear All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Single Entry Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="mx-4 max-w-md rounded-xl bg-white p-6 shadow-xl dark:bg-gray-800">
            <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
              Delete Chat?
            </h3>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              This will permanently delete this conversation. This action cannot
              be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="rounded-lg bg-red-500 px-4 py-2 text-sm text-white transition-colors hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
