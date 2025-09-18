import weaviate, { WeaviateClient } from "weaviate-ts-client";
import { parseEnv } from "./types";

export function getClient(): WeaviateClient {
  const env = parseEnv();
  const url = new URL(env.WEAVIATE_URL);
  const scheme = url.protocol.replace(":", "");
  const host = url.host;
  return weaviate.client({
    scheme,
    host,
    apiKey: new (weaviate as any).ApiKey(env.WEAVIATE_API_KEY),
  });
}

export async function getClass(client: WeaviateClient, className: string) {
  const schema = await client.schema.getter().do();
  const classes = (schema as any).classes || [];
  return classes.find((c: any) => c.class === className);
}

export async function ensureClass(client: WeaviateClient, className: string, _embeddingDim: number): Promise<void> {
  const existing = await getClass(client, className);
  if (existing) return;
  await client.schema.classCreator().withClass({
    class: className,
    vectorizer: "none",
    vectorIndexType: "hnsw",
    vectorIndexConfig: { distance: "cosine" },
    properties: [
      { name: "content", dataType: ["text"] },
      { name: "source", dataType: ["text"] },
      { name: "title", dataType: ["text"] },
      { name: "doc_id", dataType: ["text"] },
      { name: "chunk_index", dataType: ["int"] },
    ],
  } as any).do();
}