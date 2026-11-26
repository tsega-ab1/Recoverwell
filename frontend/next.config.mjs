/** @type {import('next').NextConfig} */
const isPages = process.env.GITHUB_ACTIONS === "true";

const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  ...(isPages ? { basePath: "/Recoverwell", assetPrefix: "/Recoverwell/" } : {}),
};

export default nextConfig;