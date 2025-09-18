import dotenv from "dotenv";
import { v4 as uuidv4 } from "uuid";
import { chunkText } from "./chunk";
import { embedText, getEmbeddingDim } from "./embeddings";
import { getClient, ensureClass } from "./weaviate";
import { extractTitle, makeDocId, readUtf8, walkFiles } from "./util";
import { parseEnv } from "./types";

async function main() {
  dotenv.config();
  const env = parseEnv();
  const client = getClient();

  const dim = await getEmbeddingDim();
  console.log(`Embedding dimension: ${dim}`);
  await ensureClass(client, env.WEAVIATE_CLASS, dim);

  const dirFlagIndex = process.argv.findIndex((a) => a === "--dir");
  const dir = dirFlagIndex !== -1 ? process.argv[dirFlagIndex + 1] : "./data";

  const files = await walkFiles(dir);
  console.log(`Found ${files.length} files to ingest`);

  let totalChunks = 0;
  for (const file of files) {
    try {
      const content = await readUtf8(file);
      const title = extractTitle(content, file);
      const docId = makeDocId(file);
      const chunks = chunkText(content, 3200, 400);

      let idx = 0;
      for (const chunk of chunks) {
        const vector = await embedText(chunk);
        await client.data
          .creator()
          .withClassName(env.WEAVIATE_CLASS)
          .withId(uuidv4())
          .withProperties({ content: chunk, source: file, title, doc_id: docId, chunk_index: idx })
          .withVector(vector)
          .do();
        idx++;
        totalChunks++;
      }
      console.log(`Ingested ${idx} chunks from ${file}`);
    } catch (err: any) {
      console.error(`Failed to ingest ${file}:`, err.message || err);
      throw err;
    }
  }

  console.log(`Done. Total chunks: ${totalChunks}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});