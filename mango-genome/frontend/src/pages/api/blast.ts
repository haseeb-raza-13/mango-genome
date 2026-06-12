import type { NextApiRequest, NextApiResponse } from "next";
import { logger } from "@/src/lib/logger";

export const config = {
  api: { bodyParser: false },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const fastapiUrl = process.env.FASTAPI_URL ?? "http://localhost:8000";
  const contentType = req.headers["content-type"] ?? "";

  logger.info("blast proxy → FastAPI", { contentType: contentType.split(";")[0] });

  try {
    // Collect the raw body chunks (multipart form data)
    const chunks: Buffer[] = [];
    for await (const chunk of req) {
      chunks.push(typeof chunk === "string" ? Buffer.from(chunk) : chunk);
    }
    const body = Buffer.concat(chunks);

    const upstream = await fetch(`${fastapiUrl}/blast/search`, {
      method: "POST",
      headers: {
        "content-type": contentType,
        "content-length": String(body.length),
      },
      body,
      // Allow long-running BLAST jobs (up to 5 minutes)
      signal: AbortSignal.timeout(300_000),
    });

    const data = await upstream.json();
    logger.info("blast proxy response", { status: upstream.status, hits: (data as any)?.total_hits });
    return res.status(upstream.status).json(data);
  } catch (err) {
    logger.error("blast proxy failed", err);
    if (err instanceof Error && err.name === "TimeoutError") {
      return res.status(504).json({ error: "BLAST timed out (>5 min). Try a shorter sequence or a specific database." });
    }
    return res.status(502).json({ error: "Backend unavailable" });
  }
}
