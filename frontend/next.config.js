/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
  experimental: {
    serverActions: true,
  },
  env: {
    NEXT_PUBLIC_BACKEND_URL:
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      'https://api.sodmaster.online',
    NEXT_PUBLIC_TG_GATEWAY_URL:
      process.env.NEXT_PUBLIC_TG_GATEWAY_URL || 'https://tg.sodmaster.online',
    NEXT_PUBLIC_WA_GATEWAY_URL:
      process.env.NEXT_PUBLIC_WA_GATEWAY_URL || 'https://wa.sodmaster.online',
  },
  images: {
    domains: [],
  },
};

module.exports = nextConfig;
