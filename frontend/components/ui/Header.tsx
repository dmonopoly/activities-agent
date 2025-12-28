'use client';

import Link from 'next/link';

interface HeaderProps {
  userId?: string;
}

export default function Header({ userId }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-[#FF385D]">
            Activities Agent
          </Link>
          <div className="flex items-center gap-6">
            <nav className="flex gap-6">
              <Link href="/" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                New Chat
              </Link>
              <Link href="/history" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Chat History
              </Link>
              {/* TODO: Enable when ready <Link href="/activities" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Browse Activities
              </Link> */}
              <Link href="/preferences" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Preferences
              </Link>
            </nav>
            {userId && (
              <Link href="/preferences" className="flex items-center gap-2 pl-6 border-l border-gray-200 hover:opacity-80 transition-opacity">
                <span className="text-xs text-gray-400">User:</span>
                <span className="px-2 py-1 bg-pink-50 text-pink-700 text-xs font-medium rounded-full max-w-[150px] truncate" title={userId}>
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

