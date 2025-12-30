"use client";

import { useEffect, useState } from "react";

import ActivityChat from "@/components/chat/ActivityChat";
import ActivityCard from "@/components/ui/ActivityCard";
import Header from "@/components/ui/Header";
import { Activity, api } from "@/lib/api";

export default function ActivitiesPage() {
  const [userId, setUserId] = useState<string>("");
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const id = localStorage.getItem("userId") || "";
    setUserId(id);
    if (id) {
      loadActivities(id);
    } else {
      setLoading(false);
    }
  }, []);

  const loadActivities = async (id: string) => {
    try {
      setLoading(true);
      const data = await api.getActivities(query, undefined, id);
      setActivities(data);
    } catch (error) {
      console.error("Error loading activities:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (userId) {
      loadActivities(userId);
    }
  };

  const handleAddToSheet = (activity: Activity) => {
    // TODO: This would trigger the agent to save to sheets. For now, just show a message.
    alert(
      `Added "${activity.name}" to your activity list! Use the chat to save to Google Sheets.`
    );
  };

  return (
    <div className="min-h-screen bg-white">
      <Header userId={userId} />

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Search Bar */}
        <div className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search for activities..."
              className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder:text-gray-400 focus:ring-2 focus:ring-pink-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
            />
            <button
              onClick={handleSearch}
              className="rounded-lg bg-rose-600 px-6 py-3 font-medium text-white transition-colors hover:bg-rose-700"
            >
              Search
            </button>
            <button
              onClick={() => setChatOpen(!chatOpen)}
              className={`rounded-lg px-6 py-3 font-medium transition-colors ${
                chatOpen
                  ? "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  : "bg-rose-100 text-rose-700 hover:bg-rose-200"
              }`}
            >
              {chatOpen ? "✕ Close Chat" : "💬 Open Assistant"}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Activities Grid */}
          <div className={`${chatOpen ? "lg:col-span-2" : "lg:col-span-3"}`}>
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-rose-600"></div>
              </div>
            ) : activities.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-lg text-gray-500">No activities found</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
                {activities.map((activity, idx) => (
                  <ActivityCard
                    key={idx}
                    {...activity}
                    onAddToSheet={() => handleAddToSheet(activity)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Collapsible Chat Panel */}
          {chatOpen && (
            <div className="lg:col-span-1">
              <div
                className="sticky top-24 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg"
                style={{ height: "calc(100vh - 250px)", minHeight: "500px" }}
              >
                <div className="border-b border-gray-200 bg-rose-50 p-4">
                  <h3 className="font-semibold text-gray-900">
                    Activity Assistant
                  </h3>
                  <p className="text-sm text-gray-600">
                    Ask me to filter or find activities!
                  </p>
                </div>
                <ActivityChat userId={userId} />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
