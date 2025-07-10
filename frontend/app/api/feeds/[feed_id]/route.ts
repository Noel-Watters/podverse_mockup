// /app/api/feeds/[feed_id]/route.ts
import axios from "axios";
import { NextResponse } from "next/server";
import { auth0 } from "@/lib/auth0";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

//Fetch a specific feed by ID
export async function GET(_request: Request, context: any) {

  const { feed_id } = context.params;
  const url = `${BACKEND_URL}/admin/feeds/${feed_id}`;
  console.log("API route /api/feeds/id called with URL:", url);
  try {
    const response = await axios.get(`${BACKEND_URL}/admin/feeds/${feed_id}`);
    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    console.error("API route error:", error, error?.stack);
    return NextResponse.json(
      { error: error.message || "Failed to fetch feed" },
      { status: error.response?.status || 500 }
    );
  }
}

//Update a specific feed by ID
export async function PUT(request: Request, context: any) {
  const { feed_id } = context.params;
  const session = await auth0.getSession();
  const data = await request.json();
  try {
    const response = await axios.put(`${BACKEND_URL}/admin/feeds/${feed_id}`, data);
    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to update feed" },
      { status: error.response?.status || 500 }
    );
  }
}

//Delete a specific feed by ID
export async function DELETE(_request: Request, context: any) {
  const { feed_id } = context.params;
  const session = await auth0.getSession();
  try {
    const response = await axios.delete(`${BACKEND_URL}/admin/feeds/${feed_id}`);
    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to delete feed" },
      { status: error.response?.status || 500 }
    );
  }
}

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