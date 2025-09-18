import axios from "axios";
import { parseEnv } from "./types";

const VOYAGE_ENDPOINT = "https://api.voyageai.com/v1/embeddings";

export async function embedTexts(texts: string[], model = "voyage-2"): Promise<number[][]> {
  const env = parseEnv();
  if (!env.VOYAGE_API_KEY) throw new Error("Missing VOYAGE_API_KEY");
  if (!Array.isArray(texts) || texts.length === 0) return [];

  try {
    const res = await axios.post(
      VOYAGE_ENDPOINT,
      { model, input: texts },
      { headers: { Authorization: `Bearer ${env.VOYAGE_API_KEY}` } }
    );
    const vectors = res.data?.data?.map((d: any) => d.embedding) as number[][];
    if (!vectors || !Array.isArray(vectors)) {
      throw new Error("Voyage embeddings response missing data");
    }
    return vectors;
  } catch (err: any) {
    const status = err?.response?.status;
    const body = JSON.stringify(err?.response?.data || err.message);
    throw new Error(`Voyage embeddings error: status=${status} body=${body}`);
  }
}

export async function embedText(text: string, model = "voyage-2"): Promise<number[]> {
  const [vec] = await embedTexts([text], model);
  return vec;
}

export async function getEmbeddingDim(model = "voyage-2"): Promise<number> {
  const vec = await embedText("dimension probe", model);
  return vec.length;
}