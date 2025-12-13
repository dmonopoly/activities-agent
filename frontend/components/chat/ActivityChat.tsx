'use client';

import { useState, useRef, useEffect } from 'react';
import { api, ChatResponse } from '@/lib/api';
import ActivityCard from '@/components/ui/ActivityCard';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ActivityChatProps {
  userId?: string;
}

export default function ActivityChat({ userId = 'default' }: ActivityChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || loading) return;

    const userMessage = messageText.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response: ChatResponse = await api.chat(userMessage, userId, conversationId);
      
      if (response.response) {
        setMessages((prev) => [...prev, { role: 'assistant', content: response.response }]);
      }

      // Extract activities from tool results if any
      const activities = response.tool_results?.find(
        (tr) => tr.tool === 'scrape_activities'
      )?.result?.activities;

      if (activities && activities.length > 0) {
        // Display activities as cards
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `Here are ${activities.length} activities I found:`,
          },
        ]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMessage(input);
  };

  const handleChipClick = (query: string) => {
    sendMessage(query);
  };

  const hasMessages = messages.length > 0;
  const suggestionChips = [
    "What should I do this weekend based on the weather and my interests?",
    "Find me outdoor activities near me",
    "Show me family-friendly events this week",
    "What are some budget-friendly activities?",
  ];

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {!hasMessages ? (
        <>
          {/* Empty State - Header and Input positioned higher */}
          <div className="flex-1 flex flex-col items-center justify-start pt-12">
            <div className="text-center text-gray-500 mb-8">
              <h2 className="text-2xl font-semibold mb-2">What can I help with?</h2>
            </div>

            {/* Suggestion Chips */}
            <div className="w-full px-6 mb-6">
              <div className="flex flex-wrap gap-2 justify-center max-w-3xl mx-auto">
                {suggestionChips.map((chip, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleChipClick(chip)}
                    disabled={loading}
                    className="px-4 py-2 text-sm bg-white border border-gray-200 rounded-full hover:border-rose-300 hover:bg-rose-50 text-gray-700 hover:text-rose-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Form - Positioned higher */}
            <div className="w-full px-6 pb-6">
              <form onSubmit={handleSend}>
                <div className="relative max-w-3xl mx-auto">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about activities..."
                    className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-rose-500 shadow-sm"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-rose-500 text-white hover:bg-rose-600 disabled:opacity-0 disabled:pointer-events-none transition-all duration-200 shadow-sm hover:shadow-md ${
                      input.trim() ? 'opacity-100' : 'opacity-0 pointer-events-none'
                    }`}
                    aria-label="Send message"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="w-5 h-5"
                    >
                      <path d="m22 2-7 20-4-9-9-4Z" />
                      <path d="M22 2 11 13" />
                    </svg>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Messages - When conversation exists */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-rose-500 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl px-4 py-3">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Container - Sticky at bottom when messages exist */}
          <div className="sticky bottom-0 border-t border-gray-200 bg-white z-10">
            <form onSubmit={handleSend} className="p-4">
              <div className="relative max-w-3xl mx-auto">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about activities..."
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-rose-500 shadow-sm"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-rose-500 text-white hover:bg-rose-600 disabled:opacity-0 disabled:pointer-events-none transition-all duration-200 shadow-sm hover:shadow-md ${
                    input.trim() ? 'opacity-100' : 'opacity-0 pointer-events-none'
                  }`}
                  aria-label="Send message"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="w-5 h-5"
                  >
                    <path d="m22 2-7 20-4-9-9-4Z" />
                    <path d="M22 2 11 13" />
                  </svg>
                </button>
              </div>
            </form>
          </div>
        </>
      )}
    </div>
  );
}
