/**
 * API client for backend communication
 */
function getApiBaseUrl(): string {
  // 1. Explicit API URL - set this in Vercel for production only
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // 2. Vercel preview deployment - derive backend URL from frontend URL
  // Frontend: activities-agent-frontend-git-{branch}-{owner}.vercel.app
  // Backend:  activities-agent-api-git-{branch}-{owner}.vercel.app
  if (
    process.env.NEXT_PUBLIC_VERCEL_ENV === "preview" &&
    process.env.NEXT_PUBLIC_VERCEL_BRANCH_URL
  ) {
    const backendUrl = process.env.NEXT_PUBLIC_VERCEL_BRANCH_URL.replace(
      "activities-agent-frontend",
      "activities-agent-api"
    );
    console.log("Preview Mode detected; backend URL:", backendUrl);
    return `https://${backendUrl}/api`;
  }

  // 3. Local development fallback
  return 'http://localhost:8000/api';
}

const API_BASE_URL = getApiBaseUrl();

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
}

export interface ChatHistoryMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatHistoryEntry {
  id: string;
  title: string;
  messages: ChatHistoryMessage[];
  created_at: string;
  updated_at: string;
}

export interface ChatHistoryListItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
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

  // Chat History APIs
  async getChatHistories(): Promise<ChatHistoryListItem[]> {
    const response = await fetch(`${API_BASE_URL}/chat-history`);
    if (!response.ok) {
      throw new Error(`Chat history API error: ${response.statusText}`);
    }
    return response.json();
  },

  async getChatHistory(id: string): Promise<ChatHistoryEntry> {
    const response = await fetch(`${API_BASE_URL}/chat-history/${id}`);
    if (!response.ok) {
      throw new Error(`Chat history API error: ${response.statusText}`);
    }
    return response.json();
  },

  async saveChatHistory(
    id: string | null,
    messages: ChatHistoryMessage[]
  ): Promise<ChatHistoryEntry> {
    const response = await fetch(`${API_BASE_URL}/chat-history`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id,
        messages,
      }),
    });

    if (!response.ok) {
      throw new Error(`Save chat history API error: ${response.statusText}`);
    }

    return response.json();
  },

  async deleteChatHistory(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chat-history/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(`Delete chat history API error: ${response.statusText}`);
    }
  },

  async clearAllChatHistory(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chat-history`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(`Clear chat history API error: ${response.statusText}`);
    }
  },
};
