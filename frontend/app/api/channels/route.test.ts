import { GET } from './route';
import { NextRequest } from 'next/server';

describe('/api/channels API Route', () => {
  beforeAll(() => {
    // @ts-ignore
    global.fetch = jest.fn();
  });

  afterEach(() => {
    // @ts-ignore
    global.fetch.mockClear();
  });

  it('GET returns all channels', async () => {
    // Mock fetch to return a successful response
    // @ts-ignore
    global.fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ data: [{ id: 1, title: 'Channel 1' }] }),
    });

    const req = {
      nextUrl: {
        searchParams: {
          toString: () => "",
        },
      },
    } as unknown as NextRequest;

    const res = await GET(req);
    const json = await res.json();
    expect(res.status).toBe(200);
    expect(Array.isArray(json)).toBe(true);
    expect(json[0]).toHaveProperty('title', 'Channel 1');
  });
});
