import { z } from "zod";

export const EnvSchema = z.object({
  VOYAGE_API_KEY: z.string().min(1),
  WEAVIATE_URL: z.string().url(),
  WEAVIATE_API_KEY: z.string().min(1),
  WEAVIATE_CLASS: z.string().default("DnDChunk"),
  DEFAULT_TOP_K: z.coerce.number().int().positive().default(5),
  PORT: z.coerce.number().int().positive().optional(),
});

export type EnvConfig = z.infer<typeof EnvSchema>;

export function parseEnv(): EnvConfig {
  const parsed = EnvSchema.safeParse(process.env);
  if (!parsed.success) {
    const issues = parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ");
    throw new Error(`Invalid environment variables: ${issues}`);
  }
  return parsed.data;
}

export const RetrieveSchema = z.object({
  query: z.string().min(1),
  topK: z.number().int().positive().optional(),
});
export type RetrieveRequest = z.infer<typeof RetrieveSchema>;

export interface ContextChunk {
  content: string;
  source: string;
  title: string;
  distance?: number;
  score?: number;
}