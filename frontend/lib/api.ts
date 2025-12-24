/**
 * API client for backend communication
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface ChatMessage {
  message: string;
  user_id?: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  tool_results?: Array<{
    tool: string;
    result: any;
  }>;
}

export interface Activity {
  name: string;
  location: string;
  date?: string;
  description?: string;
  price?: string;
  url?: string;
  image_url?: string;
}

export interface UserPreferences {
  user_id: string;
  location?: string;
  interests?: string[];
  budget_min?: number;
  budget_max?: number;
  date_preferences?: string;
}

export const api = {
  async getAllUsers(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/users`);
    if (!response.ok) {
      throw new Error(`Get All Users API error: ${response.statusText}`);
    }
    const data = await response.json();
    return data.users || [];
  },

  async chat(
    message: string,
    user_id: string = "default",
    conversation_id?: string
  ): Promise<ChatResponse> {
    console.log("Chatting:", message, user_id, conversation_id);
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        user_id,
        conversation_id,
      }),
    });

    console.log("Response:", response);
    if (!response.ok) {
      throw new Error(`Chat API error: ${response.statusText}`);
    }

    return response.json();
  },

  async getPreferences(user_id: string): Promise<UserPreferences> {
    const response = await fetch(`${API_BASE_URL}/preferences/${user_id}`);
    if (!response.ok) {
      throw new Error(`Preferences API error: ${response.statusText}`);
    }
    const data = await response.json();
    return data.preferences || data;
  },

  async updatePreferences(
    user_id: string,
    preferences: Partial<UserPreferences>
  ): Promise<UserPreferences> {
    console.log("Updating preferences:", preferences);

    const response = await fetch(`${API_BASE_URL}/preferences/${user_id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(preferences),
    });

    if (!response.ok) {
      throw new Error(`Update preferences API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.preferences || data;
  },

  async getActivities(
    query?: string,
    location?: string,
    user_id?: string
  ): Promise<Activity[]> {
    const params = new URLSearchParams();
    if (query) params.append("query", query);
    if (location) params.append("location", location);
    if (user_id) params.append("user_id", user_id);

    const response = await fetch(
      `${API_BASE_URL}/activities?${params.toString()}`
    );
    if (!response.ok) {
      throw new Error(`Activities API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.activities || [];
  },
};
