// /app/api/channels/[channel_id]/route.ts
import axios from "axios";
import { NextResponse } from "next/server";
//import { auth0 } from "@/lib/auth0";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

// Fetch a specific channel by channel ID
export async function GET(_request: Request, context: any) {
  const { channel_id } = context.params;
  const url = `${BACKEND_URL}/admin/channels/${channel_id}`;
  console.log("API route /api/channels/id called with URL:", url);
  try {
    const response = await axios.get(url);
    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    console.error("API route error:", error, error?.stack);
    return NextResponse.json(
      { error: error.message || "Failed to fetch channel" },
      { status: error.response?.status || 500 }
    );
  }
}