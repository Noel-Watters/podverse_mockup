
import axios from "axios";
import { NextResponse } from "next/server";
//import { auth0 } from "@/lib/auth0";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

// Fetch channels by feed ID(s)
export async function GET(request: Request) {
  const urlObj = new URL(request.url);
  const query = urlObj.searchParams.toString();
  const url = `${BACKEND_URL}/admin/channels/by-feed${query ? `?${query}` : ""}`;
  console.log("API route /api/channels/by-feed called with URL:", url);
  try {
    const response = await axios.get(url);
    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    console.error("API route error:", error, error?.stack);
    return NextResponse.json(
      { error: error.message || "Failed to fetch channels by feed ID(s)" },
      { status: error.response?.status || 500 }
    );
  }
}

