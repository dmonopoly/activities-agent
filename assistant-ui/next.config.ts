import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // @assistant-ui/tap resources can throw "Resource updated before mount" under
  // React Strict Mode's dev-only double-render (discarded pre-mount render).
  // Disabling Strict Mode avoids those throwaway renders in dev.
  reactStrictMode: false,
};

export default nextConfig;
