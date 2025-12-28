'use client';

import ReactMarkdown from 'react-markdown';

interface MarkdownContentProps {
  content: string;
}

export default function MarkdownContent({ content }: MarkdownContentProps) {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        components={{
          h1: ({ children }) => (
            <h1 className="text-xl font-bold mb-3 mt-4 first:mt-0 text-gray-900">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold mb-2 mt-3 first:mt-0 text-gray-900">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold mb-2 mt-3 first:mt-0 text-gray-900">{children}</h3>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-rose-600">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-gray-700">{children}</em>
          ),
          ul: ({ children }) => (
            <ul className="list-disc pl-5 space-y-1.5 my-2">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal pl-5 space-y-1.5 my-2">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="text-gray-800 leading-relaxed">{children}</li>
          ),
          p: ({ children }) => (
            <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-rose-500 hover:text-rose-600 underline"
            >
              {children}
            </a>
          ),
          code: ({ children }) => (
            <code className="bg-gray-200 px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-rose-300 pl-4 my-2 italic text-gray-600">
              {children}
            </blockquote>
          ),
          hr: () => <hr className="my-4 border-gray-300" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

