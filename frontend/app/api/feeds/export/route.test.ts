import axios from "axios";
import { GET } from "./route";
import { NextRequest } from "next/server";

jest.mock("axios");

describe("GET /api/feeds/export", () => {
  const mockSearchParams = new URLSearchParams({ format: "csv" });
  const mockReq = {
    nextUrl: { searchParams: mockSearchParams }
  } as unknown as NextRequest;

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("returns CSV file with correct headers", async () => {
    (axios.get as jest.Mock).mockResolvedValue({
      data: Buffer.from("id,name\n1,Feed1"),
      status: 200,
      headers: {
        "content-type": "text/csv",
        "content-disposition": "attachment; filename=feeds_export.csv"
      }
    });

    const res = await GET(mockReq);
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toBe("text/csv");
    expect(res.headers.get("Content-Disposition")).toBe("attachment; filename=feeds_export.csv");
  });

  it("returns JSON file with correct headers", async () => {
    mockSearchParams.set("format", "json");
    (axios.get as jest.Mock).mockResolvedValue({
      data: Buffer.from(JSON.stringify([{ id: 1, name: "Feed1" }])),
      status: 200,
      headers: {
        "content-type": "application/json",
        "content-disposition": "attachment; filename=feeds_export.json"
      }
    });

    const res = await GET(mockReq);
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toBe("application/json");
    expect(res.headers.get("Content-Disposition")).toBe("attachment; filename=feeds_export.json");
  });

  it("handles errors gracefully", async () => {
    (axios.get as jest.Mock).mockRejectedValue({ message: "Export failed", response: { status: 500 } });
    const res = await GET(mockReq);
    expect(res.status).toBe(500);
  });
});