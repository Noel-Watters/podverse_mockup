// /app/api/feeds/[feed_id]/route.ts
import axios from "axios";
import { NextResponse } from "next/server";
import { auth0 } from "@/lib/auth0";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";


//Reparse a specific feed by ID
export async function POST(_request: Request, context: any) {
  const { feed_id } = context.params;
  const session = await auth0.getSession();
  try {
    const response = await axios.post(`${BACKEND_URL}/admin/feeds/${feed_id}/reparse`);
    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to reparse feed" },
      { status: error.response?.status || 500 }
    );
  }
}