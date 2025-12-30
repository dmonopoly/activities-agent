'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { api, ChatResponse, ChatHistoryMessage } from '@/lib/api';
import ActivityCard from '@/components/ui/ActivityCard';
import MarkdownContent from '@/components/ui/MarkdownContent';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ActivityChatProps {
  userId?: string;
  historyId?: string | null;
  initialMessages?: Message[];
  onHistoryChange?: (historyId: string) => void;
}

const SendIcon = () => (
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
    <path d="M12 19V5M5 12l7-7 7 7" />
  </svg>
);

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  containerClassName?: string;
  formClassName?: string;
}

const ChatInput = ({ input, setInput, onSubmit, loading, containerClassName = '', formClassName = '' }: ChatInputProps) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift), but allow Shift+Enter for new line
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !loading) {
        onSubmit(e);
      }
    }
  };

  return (
    <div className={containerClassName}>
      <form onSubmit={onSubmit} className={formClassName}>
        <div className="relative max-w-3xl mx-auto">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about activities..."
            className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-3xl focus:outline-none focus:ring-2 focus:ring-rose-500 shadow-sm resize-none overflow-hidden min-h-[48px] max-h-[200px] leading-6 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
            disabled={loading}
            rows={1}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className={`absolute right-2 bottom-2 p-2 rounded-full bg-rose-500 text-white hover:bg-rose-600 disabled:opacity-0 disabled:pointer-events-none transition-all duration-200 shadow-sm hover:shadow-md ${
              input.trim() ? 'opacity-100' : 'opacity-0 pointer-events-none'
            }`}
            aria-label="Send message"
          >
            <SendIcon />
          </button>
        </div>
      </form>
    </div>
  );
};

export default function ActivityChat({ 
  userId = 'default', 
  historyId: initialHistoryId = null,
  initialMessages = [],
  onHistoryChange
}: ActivityChatProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [currentHistoryId, setCurrentHistoryId] = useState<string | null>(initialHistoryId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (initialMessages.length > 0) {
      setMessages(initialMessages);
    }
  }, [initialMessages]);

  useEffect(() => {
    setCurrentHistoryId(initialHistoryId);
  }, [initialHistoryId]);

  const saveHistory = useCallback(async (updatedMessages: Message[]) => {
    if (updatedMessages.length === 0) return;

    try {
      const result = await api.saveChatHistory(
        currentHistoryId,
        updatedMessages as ChatHistoryMessage[]
      );
      
      // Update history ID if new
      if (result.id !== currentHistoryId) {
        setCurrentHistoryId(result.id);
        onHistoryChange?.(result.id);
      }
    } catch (error) {
      console.error('Failed to save chat history:', error);
    }
  }, [currentHistoryId, onHistoryChange]);

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || loading) return;

    const userMessage = messageText.trim();
    setInput('');
    const newMessages: Message[] = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response: ChatResponse = await api.chat(userMessage, userId, conversationId);
      
      let finalMessages = newMessages;
      
      if (response.response) {
        finalMessages = [...newMessages, { role: 'assistant', content: response.response }];
        setMessages(finalMessages);
      }

      // Extract activities from tool results if any
      const activities = response.tool_results?.find(
        (tr) => tr.tool === 'scrape_activities'
      )?.result?.activities;

      if (activities && activities.length > 0) {
        // Display activities as cards
        finalMessages = [
          ...finalMessages,
          {
            role: 'assistant',
            content: `Here are ${activities.length} activities I found:`,
          },
        ];
        setMessages(finalMessages);
      }

      await saveHistory(finalMessages);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessages: Message[] = [
        ...newMessages,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ];
      setMessages(errorMessages);
      await saveHistory(errorMessages);
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
    <div className="flex flex-col h-full w-full max-w-4xl mx-auto bg-white dark:bg-gray-900">
      {!hasMessages ? (
        <>
          {/* Empty State - Header and Input positioned higher */}
          <div className="flex-1 flex flex-col items-center justify-start pt-16 min-h-0 bg-white dark:bg-gray-900">
            <div className="text-center text-gray-500 dark:text-gray-400 mb-8">
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
                    className="px-4 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full hover:border-rose-300 dark:hover:border-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 text-gray-700 dark:text-gray-300 hover:text-rose-600 dark:hover:text-rose-400 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Form - Positioned higher */}
            <ChatInput
              input={input}
              setInput={setInput}
              onSubmit={handleSend}
              loading={loading}
              containerClassName="w-full px-6 pb-6"
            />
          </div>
        </>
      ) : (
        <>
          {/* Messages - When conversation exists */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-white dark:bg-gray-900">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-rose-500 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                  }`}
                >
                  {message.role === 'assistant' ? (
                    <MarkdownContent content={message.content} />
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl px-4 py-3">
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
          <ChatInput
            input={input}
            setInput={setInput}
            onSubmit={handleSend}
            loading={loading}
            containerClassName="sticky bottom-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 z-10"
            formClassName="p-4"
          />
        </>
      )}
    </div>
  );
}
