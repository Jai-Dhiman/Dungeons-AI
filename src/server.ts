import dotenv from "dotenv";
import express from "express";
import { embedText } from "./embeddings";
import { getClient } from "./weaviate";
import { ContextChunk, RetrieveSchema, parseEnv } from "./types";

dotenv.config();
const env = parseEnv();
const app = express();
app.use(express.json());
const client = getClient();

app.get("/health", (_req, res) => {
  res.json({ ok: true });
});

app.post("/retrieve", async (req, res) => {
  const parsed = RetrieveSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: parsed.error.flatten() });
  const { query, topK } = parsed.data;
  const k = topK ?? env.DEFAULT_TOP_K;

  try {
    const vector = await embedText(query);
    const gql = await client.graphql
      .get()
      .withClassName(env.WEAVIATE_CLASS)
      .withLimit(k)
      .withNearVector({ vector })
      .withFields("content source title doc_id chunk_index _additional { id distance }")
      .do();

    const items = (gql as any)?.data?.Get?.[env.WEAVIATE_CLASS] || [];
    const contexts: ContextChunk[] = items.map((it: any) => ({
      content: it.content,
      source: it.source,
      title: it.title,
      distance: it._additional?.distance,
    }));

    res.json({ contexts, topK: k });
  } catch (err: any) {
    const status = err?.response?.status || 500;
    const body = err?.response?.data || { message: err.message };
    res.status(status >= 400 && status < 600 ? 502 : 500).json({ error: body });
  }
});

const port = env.PORT ?? 3001;
app.listen(port, () => {
  console.log(`RAG server listening on http://localhost:${port}`);
});