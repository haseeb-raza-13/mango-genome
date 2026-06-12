import type { NextApiRequest, NextApiResponse } from "next";
import { logger } from "@/src/lib/logger";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const fastapiUrl = process.env.FASTAPI_URL ?? "http://localhost:8000";
  logger.info("blast-databases proxy → FastAPI");

  try {
    const upstream = await fetch(`${fastapiUrl}/blast/databases`, { method: "GET" });
    const data = await upstream.json();
    logger.info("blast-databases response", { status: upstream.status });
    return res.status(upstream.status).json(data);
  } catch (err) {
    logger.error("blast-databases proxy failed", err);
    return res.status(502).json({ error: "Backend unavailable" });
  }
}
