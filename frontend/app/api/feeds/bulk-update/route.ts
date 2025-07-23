import axios from "axios";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

// Bulk update feed status
export async function POST(req: NextRequest) {
  try {
    const data = await req.json(); 
    const response = await axios.post(`${BACKEND_URL}/admin/feeds/bulk-update`, data);
    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to bulk update feed status" },
      { status: error.response?.status || 500 }
    );
  }
}