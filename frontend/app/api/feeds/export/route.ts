import axios from "axios";
import { NextRequest, NextResponse } from "next/server";
//import { auth0 } from "@/lib/auth0";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

//Exoport Feeds
export async function GET(req: NextRequest) {
  const query = req.nextUrl.searchParams.toString();
  const url = `${BACKEND_URL}/admin/feeds/export${query ? `?${query}` : ""}`;
  console.log("API route /api/feeds/export called with URL:", url);
  try {
    const response = await axios.get(url, { responseType: "arraybuffer" });
    // If backend returns CSV, set correct headers
    const contentType = response.headers["content-type"] || "application/octet-stream";
    return new NextResponse(response.data, {
      status: response.status,
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": response.headers["content-disposition"] || "attachment; filename=feeds_export.csv"
      }
    });
  } catch (error: any) {
    console.error("API route error:", error, error?.stack);
    return NextResponse.json(
      { error: error.message || "Failed to export feeds" },
      { status: error.response?.status || 500 }
    );
  }
}
