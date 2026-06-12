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

  logger.info("msa proxy → FastAPI", { contentType: contentType.split(";")[0] });

  try {
    const chunks: Buffer[] = [];
    for await (const chunk of req) {
      chunks.push(typeof chunk === "string" ? Buffer.from(chunk) : chunk);
    }
    const body = Buffer.concat(chunks);

    const upstream = await fetch(`${fastapiUrl}/msa/align`, {
      method: "POST",
      headers: {
        "content-type": contentType,
        "content-length": String(body.length),
      },
      body,
      signal: AbortSignal.timeout(300_000),
    });

    const data = await upstream.json();
    logger.info("msa proxy response", { status: upstream.status });
    return res.status(upstream.status).json(data);
  } catch (err) {
    logger.error("msa proxy failed", err);
    if (err instanceof Error && err.name === "TimeoutError") {
      return res.status(504).json({ error: "MSA timed out. Try fewer or shorter sequences." });
    }
    return res.status(502).json({ error: "Backend unavailable" });
  }
}
