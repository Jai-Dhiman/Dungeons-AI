export function chunkText(text: string, chunkSize = 3200, overlap = 400): string[] {
  const chunks: string[] = [];
  const len = text.length;
  if (len === 0) return chunks;
  if (len <= chunkSize) return [text.trim()];

  let start = 0;
  while (start < len) {
    const targetEnd = Math.min(start + chunkSize, len);
    let end = targetEnd;

    // Try to break on whitespace near the end
    const searchStart = Math.max(start + chunkSize - 200, start);
    let foundBreak = -1;
    for (let i = targetEnd; i >= searchStart; i--) {
      const c = text[i];
      if (c === " " || c === "\n" || c === "\t") {
        foundBreak = i;
        break;
      }
    }
    if (foundBreak !== -1 && foundBreak > start) {
      end = foundBreak;
    }

    const piece = text.slice(start, end).trim();
    if (piece.length > 0) chunks.push(piece);

    if (end >= len) break;
    const nextStart = Math.max(end - overlap, start + 1); // ensure progress
    if (nextStart <= start) break; // safety
    start = nextStart;
  }

  return chunks;
}