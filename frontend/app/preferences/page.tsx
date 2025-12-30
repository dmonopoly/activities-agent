"use client";

import { useEffect, useState } from "react";

import Header from "@/components/ui/Header";
import { api, UserPreferences } from "@/lib/api";

export default function PreferencesPage() {
  const [userId, setUserId] = useState<string>("");
  const [allUsers, setAllUsers] = useState<string[]>([]);
  const [preferences, setPreferences] = useState<Partial<UserPreferences>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadAllUsers();
  }, []);

  const loadAllUsers = async () => {
    try {
      const users = await api.getAllUsers();
      setAllUsers(users);

      // Check if there's a saved user in localStorage
      let id = localStorage.getItem("userId");
      if (id && users.includes(id)) {
        setUserId(id);
        await loadPreferences(id);
      } else if (users.length > 0) {
        console.log(
          "Local storage user not found in user list, defaulting to first user"
        );
        id = users[0];
        localStorage.setItem("userId", id);
        setUserId(id);
        await loadPreferences(id);
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.error("Error loading users:", error);
      setLoading(false);
    }
  };

  const loadPreferences = async (id: string) => {
    try {
      setLoading(true);
      const prefs = await api.getPreferences(id);
      setPreferences({
        location: prefs.location || "",
        interests: prefs.interests || [],
        budget_min: prefs.budget_min || undefined,
        budget_max: prefs.budget_max || undefined,
      });
    } catch (error) {
      console.error("Error loading preferences:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUserChange = async (newUserId: string) => {
    setUserId(newUserId);
    localStorage.setItem("userId", newUserId);
    await loadPreferences(newUserId);
  };

  const handleSave = async () => {
    if (!userId) return;
    setSaving(true);
    setSaved(false);

    try {
      await api.updatePreferences(userId, preferences);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error("Error saving preferences:", error);
      alert("Failed to save preferences. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleInterestAdd = (interest: string) => {
    if (!interest.trim()) return;
    const current = preferences.interests || [];
    if (!current.includes(interest.trim())) {
      setPreferences({
        ...preferences,
        interests: [...current, interest.trim()],
      });
    }
  };

  const handleInterestRemove = (interest: string) => {
    const current = preferences.interests || [];
    setPreferences({
      ...preferences,
      interests: current.filter((i) => i !== interest),
    });
  };

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col bg-white transition-colors dark:bg-gray-900">
        <Header userId={userId} />
        <div className="flex flex-1 items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-pink-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-white transition-colors dark:bg-gray-900">
      <Header userId={userId} />

      {/* Main Content */}
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
        <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
          Your Preferences
        </h1>
        <p className="mb-8 text-gray-600 dark:text-gray-400">
          Help us find the ideal activities for you!
        </p>

        <div className="space-y-6">
          {/* User Selector */}
          <div className="rounded-lg border border-pink-100 bg-pink-50 p-4 dark:border-pink-800 dark:bg-pink-900/20">
            <label className="mb-2 block text-sm font-medium text-pink-900 dark:text-pink-300">
              Select User Profile
            </label>
            <select
              value={userId}
              onChange={(e) => handleUserChange(e.target.value)}
              className="w-full rounded-lg border border-pink-200 bg-white px-4 py-2 text-gray-900 focus:ring-2 focus:ring-pink-500 focus:outline-none dark:border-pink-700 dark:bg-gray-800 dark:text-white"
            >
              {allUsers.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
            <p className="mt-2 text-xs text-pink-600 dark:text-pink-400">
              Switching users will load their saved preferences
            </p>
          </div>

          {/* Location */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Location
            </label>
            <input
              type="text"
              value={preferences.location || ""}
              onChange={(e) =>
                setPreferences({ ...preferences, location: e.target.value })
              }
              placeholder="City, neighborhood, or area"
              className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 placeholder:text-gray-400 focus:ring-2 focus:ring-pink-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
            />
          </div>

          {/* Interests */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Interests
            </label>
            <div className="mb-2 flex gap-2">
              <input
                id="interest-input"
                type="text"
                placeholder="Add an interest (e.g., outdoor, art, music)"
                className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 placeholder:text-gray-400 focus:ring-2 focus:ring-pink-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleInterestAdd(e.currentTarget.value);
                    e.currentTarget.value = "";
                  }
                }}
              />
              <button
                type="button"
                onClick={() => {
                  const input = document.getElementById(
                    "interest-input"
                  ) as HTMLInputElement;
                  if (input && input.value) {
                    handleInterestAdd(input.value);
                    input.value = "";
                  }
                }}
                className="rounded-lg bg-pink-600 px-4 py-2 text-white transition-colors hover:bg-pink-700"
              >
                Add
              </button>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {(preferences.interests || []).map((interest) => (
                <span
                  key={interest}
                  className="inline-flex items-center gap-2 rounded-full bg-pink-100 px-3 py-1 text-sm text-pink-700 dark:bg-pink-900/40 dark:text-pink-300"
                >
                  {interest}
                  <button
                    onClick={() => handleInterestRemove(interest)}
                    className="text-pink-700 hover:text-pink-900 dark:text-pink-300 dark:hover:text-pink-100"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Budget */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Min Budget ($)
              </label>
              <input
                type="number"
                value={preferences.budget_min || ""}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    budget_min: e.target.value
                      ? parseFloat(e.target.value)
                      : undefined,
                  })
                }
                placeholder="0"
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 placeholder:text-gray-400 focus:ring-2 focus:ring-pink-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Max Budget ($)
              </label>
              <input
                type="number"
                value={preferences.budget_max || ""}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    budget_max: e.target.value
                      ? parseFloat(e.target.value)
                      : undefined,
                  })
                }
                placeholder="1000"
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 placeholder:text-gray-400 focus:ring-2 focus:ring-pink-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
              />
            </div>
          </div>

          {/* Save Button */}
          <div className="pt-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className={`w-full rounded-lg bg-pink-600 px-6 py-3 font-medium text-white transition-colors hover:bg-pink-700 disabled:cursor-not-allowed disabled:opacity-50 ${
                saved ? "bg-green-600 hover:bg-green-700" : ""
              }`}
            >
              {saved ? "✓ Saved!" : saving ? "Saving..." : "Save Preferences"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
