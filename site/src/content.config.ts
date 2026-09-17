import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

// One file per tab. The file name is the URL slug.
const tabs = defineCollection({
  loader: glob({ pattern: "*.{md,mdx}", base: "./src/content/tabs" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
  }),
});

export const collections = { tabs };
