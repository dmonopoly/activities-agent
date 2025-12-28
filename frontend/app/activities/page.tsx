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
    // This would trigger the agent to save to sheets
    // For now, just show a message
    alert(
      `Added "${activity.name}" to your activity list! Use the chat to save to Google Sheets.`
    );
  };

  return (
    <div className="min-h-screen bg-white">
      <Header userId={userId} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search for activities..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
            />
            <button
              onClick={handleSearch}
              className="px-6 py-3 bg-pink-600 text-white rounded-lg font-medium hover:bg-pink-700 transition-colors"
            >
              Search
            </button>
            <button
              onClick={() => setChatOpen(!chatOpen)}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                chatOpen
                  ? "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  : "bg-pink-100 text-pink-700 hover:bg-pink-200"
              }`}
            >
              {chatOpen ? "✕ Close Chat" : "💬 Open Assistant"}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Activities Grid */}
          <div className={`${chatOpen ? "lg:col-span-2" : "lg:col-span-3"}`}>
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
              </div>
            ) : activities.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No activities found</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
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
                className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden sticky top-24"
                style={{ height: "calc(100vh - 250px)", minHeight: "500px" }}
              >
                <div className="p-4 border-b border-gray-200 bg-pink-50">
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
