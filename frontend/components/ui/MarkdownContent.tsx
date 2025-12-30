"use client";

import ReactMarkdown from "react-markdown";

interface MarkdownContentProps {
  content: string;
}

export default function MarkdownContent({ content }: MarkdownContentProps) {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        components={{
          h1: ({ children }) => (
            <h1 className="mt-4 mb-3 text-xl font-bold text-gray-900 first:mt-0 dark:text-gray-100">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="mt-3 mb-2 text-lg font-semibold text-gray-900 first:mt-0 dark:text-gray-100">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="mt-3 mb-2 text-base font-semibold text-gray-900 first:mt-0 dark:text-gray-100">
              {children}
            </h3>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-rose-600 dark:text-rose-400">
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="text-gray-700 italic dark:text-gray-300">
              {children}
            </em>
          ),
          ul: ({ children }) => (
            <ul className="my-2 list-disc space-y-1.5 pl-5">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="my-2 list-decimal space-y-1.5 pl-5">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="leading-relaxed text-gray-800 dark:text-gray-200">
              {children}
            </li>
          ),
          p: ({ children }) => (
            <p className="mb-2 leading-relaxed text-gray-800 last:mb-0 dark:text-gray-200">
              {children}
            </p>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-rose-500 underline hover:text-rose-600 dark:text-rose-400 dark:hover:text-rose-300"
            >
              {children}
            </a>
          ),
          code: ({ children }) => (
            <code className="rounded bg-gray-200 px-1.5 py-0.5 font-mono text-sm text-gray-800 dark:bg-gray-700 dark:text-gray-200">
              {children}
            </code>
          ),
          blockquote: ({ children }) => (
            <blockquote className="my-2 border-l-4 border-rose-300 pl-4 text-gray-600 italic dark:border-rose-500 dark:text-gray-400">
              {children}
            </blockquote>
          ),
          hr: () => (
            <hr className="my-4 border-gray-300 dark:border-gray-600" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
