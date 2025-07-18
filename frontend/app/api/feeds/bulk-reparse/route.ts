import axios from "axios";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

// Bulk reparse feeds
export async function POST(req: NextRequest) {
  try {
    const data = await req.json(); // { feed_ids: [...] }
    const response = await axios.post(`${BACKEND_URL}/admin/feeds/bulk-reparse`, data);
    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to bulk reparse feeds" },
      { status: error.response?.status || 500 }
    );
  }
}