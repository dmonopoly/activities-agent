'use client';

import Image from 'next/image';

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
      <div className="relative w-full h-64 mb-3 overflow-hidden rounded-xl bg-gray-200">
        {image_url ? (
          <Image
            src={image_url}
            alt={name}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">{name.charAt(0)}</span>
          </div>
        )}
      </div>
      
      <div className="space-y-1">
        <div className="flex items-start justify-between">
          <h3 className="font-semibold text-lg text-gray-900 line-clamp-1">{name}</h3>
          {price && (
            <span className="text-gray-600 font-medium whitespace-nowrap ml-2">{price}</span>
          )}
        </div>
        
        <p className="text-gray-500 text-sm flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {location}
        </p>
        
        {date && (
          <p className="text-gray-500 text-sm">{date}</p>
        )}
        
        {description && (
          <p className="text-gray-600 text-sm line-clamp-2 mt-2">{description}</p>
        )}
        
        {onAddToSheet && (
          <button
            onClick={onAddToSheet}
            className="mt-3 w-full px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-colors text-sm font-medium"
          >
            Add to Sheet
          </button>
        )}
      </div>
    </div>
  );
}
