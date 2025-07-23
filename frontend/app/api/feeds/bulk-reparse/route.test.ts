import axios from "axios";
import { POST } from "./route";
import { NextRequest } from "next/server";

jest.mock("axios");

describe("POST /api/feeds/bulk-reparse", () => {
  const mockReq = {
    json: async () => ({ feed_ids: [1, 2, 3] })
  } as unknown as NextRequest;

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("returns success response", async () => {
    (axios.post as jest.Mock).mockResolvedValue({
      data: { success: true },
      status: 200
    });

    const res = await POST(mockReq);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ success: true });
  });

  it("handles errors gracefully", async () => {
    (axios.post as jest.Mock).mockRejectedValue({ message: "Bulk reparse failed", response: { status: 500 } });
    const res = await POST(mockReq);
    expect(res.status).toBe(500);
    expect(await res.json()).toEqual({ error: "Bulk reparse failed" });
  });
});