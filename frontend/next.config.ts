import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Expose Vercel's auto-set variables to client-side code
  // These are set by Vercel at build time but not exposed to browser by default
  env: {
    NEXT_PUBLIC_VERCEL_URL: process.env.VERCEL_URL,
    NEXT_PUBLIC_VERCEL_ENV: process.env.VERCEL_ENV,
  },
};

export default nextConfig;
