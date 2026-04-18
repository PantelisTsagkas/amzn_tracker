import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // "standalone" is only needed for Docker self-hosting;
  // Vercel uses its own adapter and doesn't need it.
  ...(process.env.VERCEL ? {} : { output: "standalone" }),
};

export default nextConfig;
