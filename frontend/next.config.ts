import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Expose Vercel's auto-set server-side process.env variables to client-side code.
  env: {
    NEXT_PUBLIC_VERCEL_ENV: process.env.VERCEL_ENV,
    NEXT_PUBLIC_VERCEL_BRANCH_URL: process.env.VERCEL_BRANCH_URL,
  },
};

export default nextConfig;
