"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import MarkdownContent from "@/components/ui/MarkdownContent";
import { api, ChatHistoryMessage, ChatResponse } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
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
    className="h-5 w-5"
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

const ChatInput = ({
  input,
  setInput,
  onSubmit,
  loading,
  containerClassName = "",
  formClassName = "",
}: ChatInputProps) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift), but allow Shift+Enter for new line
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !loading) {
        onSubmit(e);
      }
    }
  };

  return (
    <div className={containerClassName}>
      <form onSubmit={onSubmit} className={formClassName}>
        <div className="relative mx-auto max-w-3xl">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about activities..."
            className="max-h-[200px] min-h-[48px] w-full resize-none overflow-hidden rounded-3xl border border-gray-300 bg-white px-4 py-3 pr-12 leading-6 text-gray-900 shadow-sm placeholder:text-gray-400 focus:ring-2 focus:ring-rose-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
            disabled={loading}
            rows={1}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className={`absolute right-2 bottom-2 rounded-full bg-rose-500 p-2 text-white shadow-sm transition-all duration-200 hover:bg-rose-600 hover:shadow-md disabled:pointer-events-none disabled:opacity-0 ${
              input.trim() ? "opacity-100" : "pointer-events-none opacity-0"
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
  userId = "default",
  historyId: initialHistoryId = null,
  initialMessages = [],
  onHistoryChange,
}: ActivityChatProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [currentHistoryId, setCurrentHistoryId] = useState<string | null>(
    initialHistoryId
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
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

  const saveHistory = useCallback(
    async (updatedMessages: Message[]) => {
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
        console.error("Failed to save chat history:", error);
      }
    },
    [currentHistoryId, onHistoryChange]
  );

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || loading) return;

    const userMessage = messageText.trim();
    setInput("");
    const newMessages: Message[] = [
      ...messages,
      { role: "user", content: userMessage },
    ];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response: ChatResponse = await api.chat(
        userMessage,
        userId,
        conversationId
      );

      let finalMessages = newMessages;

      if (response.response) {
        finalMessages = [
          ...newMessages,
          { role: "assistant", content: response.response },
        ];
        setMessages(finalMessages);
      }

      // Extract activities from tool results if any
      const activities = response.tool_results?.find(
        (tr) => tr.tool === "scrape_activities"
      )?.result?.activities;

      if (activities && activities.length > 0) {
        // Display activities as cards
        finalMessages = [
          ...finalMessages,
          {
            role: "assistant",
            content: `Here are ${activities.length} activities I found:`,
          },
        ];
        setMessages(finalMessages);
      }

      await saveHistory(finalMessages);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessages: Message[] = [
        ...newMessages,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
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
    <div className="mx-auto flex h-full w-full max-w-4xl flex-col bg-white dark:bg-gray-900">
      {!hasMessages ? (
        <>
          {/* Empty State - Header and Input positioned higher */}
          <div className="flex min-h-0 flex-1 flex-col items-center justify-start bg-white pt-16 dark:bg-gray-900">
            <div className="mb-8 text-center text-gray-500 dark:text-gray-400">
              <h2 className="mb-2 text-2xl font-semibold">
                What can I help with?
              </h2>
            </div>

            {/* Suggestion Chips */}
            <div className="mb-6 w-full px-6">
              <div className="mx-auto flex max-w-3xl flex-wrap justify-center gap-2">
                {suggestionChips.map((chip, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleChipClick(chip)}
                    disabled={loading}
                    className="rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 shadow-sm transition-all duration-200 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-600 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:border-rose-500 dark:hover:bg-rose-900/20 dark:hover:text-rose-400"
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
          <div className="flex-1 space-y-6 overflow-y-auto bg-white p-6 dark:bg-gray-900">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === "user"
                      ? "bg-rose-500 text-white"
                      : "bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100"
                  }`}
                >
                  {message.role === "assistant" ? (
                    <MarkdownContent content={message.content} />
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-gray-100 px-4 py-3 dark:bg-gray-800">
                  <div className="flex space-x-2">
                    <div
                      className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
                      style={{ animationDelay: "0ms" }}
                    ></div>
                    <div
                      className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
                      style={{ animationDelay: "300ms" }}
                    ></div>
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
