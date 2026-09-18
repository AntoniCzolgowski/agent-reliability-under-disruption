import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";

// GitHub Pages project site: every internal URL must go through the base path.
export default defineConfig({
  site: "https://antoniczolgowski.github.io",
  base: "/agent-reliability-under-disruption",
  trailingSlash: "always",
  build: { format: "directory" },
  integrations: [mdx()],
  vite: { build: { sourcemap: true } },
});
