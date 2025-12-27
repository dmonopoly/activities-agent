'use client';

import { useState, useEffect } from 'react';
import { api, UserPreferences } from '@/lib/api';
import Header from '@/components/ui/Header';

export default function PreferencesPage() {
  const [userId, setUserId] = useState<string>('');
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
      let id = localStorage.getItem('userId');
      if (id && users.includes(id)) {
        setUserId(id);
        await loadPreferences(id);
      } else if (users.length > 0) {
        console.log('Local storage user not found in user list, defaulting to first user');
        id = users[0];
        localStorage.setItem('userId', id);
        setUserId(id);
        await loadPreferences(id);
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.error('Error loading users:', error);
      setLoading(false);
    }
  };

  const loadPreferences = async (id: string) => {
    try {
      setLoading(true);
      const prefs = await api.getPreferences(id);
      setPreferences({
        location: prefs.location || '',
        interests: prefs.interests || [],
        budget_min: prefs.budget_min || undefined,
        budget_max: prefs.budget_max || undefined,
        date_preferences: prefs.date_preferences || '',
      });
    } catch (error) {
      console.error('Error loading preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUserChange = async (newUserId: string) => {
    setUserId(newUserId);
    localStorage.setItem('userId', newUserId);
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
      console.error('Error saving preferences:', error);
      alert('Failed to save preferences. Please try again.');
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
      <div className="min-h-screen bg-white flex flex-col">
        <Header userId={userId} />
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header userId={userId} />

      {/* Main Content */}
      <main className="flex-1 max-w-3xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Preferences</h1>
        <p className="text-gray-600 mb-8">Help us find the ideal activities for you!</p>

        <div className="space-y-6">
          {/* User Selector */}
          <div className="bg-pink-50 border border-pink-100 rounded-lg p-4">
            <label className="block text-sm font-medium text-pink-900 mb-2">
              Select User Profile
            </label>
            <select
              value={userId}
              onChange={(e) => handleUserChange(e.target.value)}
              className="w-full px-4 py-2 border border-pink-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-pink-500 text-gray-900"
            >
              {allUsers.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
            <p className="text-xs text-pink-600 mt-2">
              Switching users will load their saved preferences
            </p>
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <input
              type="text"
              value={preferences.location || ''}
              onChange={(e) => setPreferences({ ...preferences, location: e.target.value })}
              placeholder="City, neighborhood, or area"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
            />
          </div>

          {/* Interests */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Interests
            </label>
            <div className="flex gap-2 mb-2">
              <input
                id="interest-input"
                type="text"
                placeholder="Add an interest (e.g., outdoor, art, music)"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleInterestAdd(e.currentTarget.value);
                    e.currentTarget.value = '';
                  }
                }}
              />
              <button
                type="button"
                onClick={() => {
                  const input = document.getElementById('interest-input') as HTMLInputElement;
                  if (input && input.value) {
                    handleInterestAdd(input.value);
                    input.value = '';
                  }
                }}
                className="px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {(preferences.interests || []).map((interest) => (
                <span
                  key={interest}
                  className="inline-flex items-center gap-2 px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-sm"
                >
                  {interest}
                  <button
                    onClick={() => handleInterestRemove(interest)}
                    className="text-pink-700 hover:text-pink-900"
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
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Budget ($)
              </label>
              <input
                type="number"
                value={preferences.budget_min || ''}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    budget_min: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
                placeholder="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Budget ($)
              </label>
              <input
                type="number"
                value={preferences.budget_max || ''}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    budget_max: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
                placeholder="1000"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
            </div>
          </div>

          {/* Date Preferences */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Time
            </label>
            <select
              value={preferences.date_preferences || ''}
              onChange={(e) =>
                setPreferences({ ...preferences, date_preferences: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
            >
              <option value="">Any time</option>
              <option value="weekend">Weekend</option>
              <option value="weekday">Weekday</option>
              <option value="evening">Evening</option>
              <option value="morning">Morning</option>
              <option value="afternoon">Afternoon</option>
            </select>
          </div>

          {/* Save Button */}
          <div className="pt-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className={`w-full px-6 py-3 bg-pink-600 text-white rounded-lg font-medium hover:bg-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
                saved ? 'bg-green-600 hover:bg-green-700' : ''
              }`}
            >
              {saved ? '✓ Saved!' : saving ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
