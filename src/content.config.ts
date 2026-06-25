import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    author: z.string().default('Nexux Pro'),
    tags: z.array(z.string()).default([]),
    faq: z.array(z.object({
      q: z.string(),
      a: z.string(),
    })).optional(),
    image: z.string().optional(),
  }),
});

export const collections = { blog };
