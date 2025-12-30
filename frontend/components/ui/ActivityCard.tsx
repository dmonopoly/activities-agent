"use client";

import Image from "next/image";

export interface ActivityCardProps {
  name: string;
  location: string;
  date?: string;
  description?: string;
  price?: string;
  url?: string;
  image_url?: string;
  onAddToSheet?: () => void;
}

export default function ActivityCard({
  name,
  location,
  date,
  description,
  price,
  url,
  image_url,
  onAddToSheet,
}: ActivityCardProps) {
  return (
    <div className="group cursor-pointer">
      <div className="relative mb-3 h-64 w-full overflow-hidden rounded-xl bg-gray-200">
        {image_url ? (
          <Image
            src={image_url}
            alt={name}
            fill
            className="object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-pink-400 to-purple-500">
            <span className="text-2xl font-bold text-white">
              {name.charAt(0)}
            </span>
          </div>
        )}
      </div>

      <div className="space-y-1">
        <div className="flex items-start justify-between">
          <h3 className="line-clamp-1 text-lg font-semibold text-gray-900">
            {name}
          </h3>
          {price && (
            <span className="ml-2 font-medium whitespace-nowrap text-gray-600">
              {price}
            </span>
          )}
        </div>

        <p className="flex items-center gap-1 text-sm text-gray-500">
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          {location}
        </p>

        {date && <p className="text-sm text-gray-500">{date}</p>}

        {description && (
          <p className="mt-2 line-clamp-2 text-sm text-gray-600">
            {description}
          </p>
        )}

        {onAddToSheet && (
          <button
            onClick={onAddToSheet}
            className="mt-3 w-full rounded-lg bg-rose-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-rose-600"
          >
            Add to Sheet
          </button>
        )}
      </div>
    </div>
  );
}
