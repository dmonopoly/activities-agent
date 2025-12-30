"use client";

import Link from "next/link";

import { useTheme } from "@/contexts/ThemeContext";

interface HeaderProps {
  userId?: string;
}

function ThemeToggle() {
  const { preference, toggleTheme } = useTheme();

  const getIcon = () => {
    switch (preference) {
      case "light":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2" />
            <path d="M12 20v2" />
            <path d="m4.93 4.93 1.41 1.41" />
            <path d="m17.66 17.66 1.41 1.41" />
            <path d="M2 12h2" />
            <path d="M20 12h2" />
            <path d="m6.34 17.66-1.41 1.41" />
            <path d="m19.07 4.93-1.41 1.41" />
          </svg>
        );
      case "dark":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
          </svg>
        );
      case "system":
      default:
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect width="20" height="14" x="2" y="3" rx="2" />
            <line x1="8" x2="16" y1="21" y2="21" />
            <line x1="12" x2="12" y1="17" y2="21" />
          </svg>
        );
    }
  };

  const getLabel = () => {
    switch (preference) {
      case "light":
        return "Light mode";
      case "dark":
        return "Dark mode";
      case "system":
        return "System theme";
    }
  };

  return (
    <button
      onClick={toggleTheme}
      className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
      title={getLabel()}
      aria-label={getLabel()}
    >
      {getIcon()}
    </button>
  );
}

export default function Header({ userId }: HeaderProps) {
  return (
    <header className="sticky top-0 z-10 border-b border-gray-200 bg-white transition-colors dark:border-gray-700 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-[#FF385D]">
            Activities Agent
          </Link>
          <div className="flex items-center gap-6">
            <nav className="flex gap-6">
              <Link
                href="/"
                className="font-medium text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
              >
                New Chat
              </Link>
              <Link
                href="/history"
                className="font-medium text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
              >
                Chat History
              </Link>
              <Link
                href="/preferences"
                className="font-medium text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
              >
                Preferences
              </Link>
            </nav>
            <ThemeToggle />
            {userId && (
              <Link
                href="/preferences"
                className="flex items-center gap-2 border-l border-gray-200 pl-6 transition-opacity hover:opacity-80 dark:border-gray-700"
              >
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  User:
                </span>
                <span
                  className="max-w-[150px] truncate rounded-full bg-rose-50 px-2 py-1 text-xs font-medium text-rose-700 dark:bg-rose-900/30 dark:text-rose-300"
                  title={userId}
                >
                  {userId}
                </span>
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
