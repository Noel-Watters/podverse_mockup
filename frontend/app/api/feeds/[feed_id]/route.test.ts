

const mockGet = jest.fn().mockResolvedValue({ data: { id: 1, title: 'Feed 1' }, status: 200 });
const mockPut = jest.fn().mockResolvedValue({ data: { id: 1, title: 'Updated Feed' }, status: 200 });
const mockDelete = jest.fn().mockResolvedValue({ data: { success: true }, status: 200 });
const mockPost = jest.fn().mockResolvedValue({ data: { reparse: true }, status: 200 });

jest.mock('axios', () => ({
  get: mockGet,
  put: mockPut,
  delete: mockDelete,
  post: mockPost,
}));

import { GET, PUT, DELETE, POST } from './route';
import { NextRequest } from 'next/server';

jest.mock('@/lib/auth0', () => ({
  auth0: { getSession: jest.fn().mockResolvedValue({ accessToken: 'fake-token' }) }
}));

const mockParams = { params: { feed_id: '1' } };

describe('/api/feeds/[feed_id] API Route', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('GET returns a feed by ID', async () => {
    const req = {} as NextRequest;
    const res = await GET(req, mockParams);
    const json = await res.json();
    expect(res.status).toBe(200);
    expect(json).toHaveProperty('id', 1);
    expect(json).toHaveProperty('title', 'Feed 1');
    expect(mockGet).toHaveBeenCalledWith(expect.stringContaining('/admin/feeds/1'));
  });

  it('PUT updates a feed by ID', async () => {
    const req = {
      json: async () => ({ title: 'Updated Feed' })
    } as unknown as NextRequest;
    const res = await PUT(req, mockParams);
    const json = await res.json();
    expect(res.status).toBe(200);
    expect(json).toHaveProperty('title', 'Updated Feed');
    expect(mockPut).toHaveBeenCalledWith(expect.stringContaining('/admin/feeds/1'), { title: 'Updated Feed' });
  });

  it('DELETE deletes a feed by ID', async () => {
    const req = {} as NextRequest;
    const res = await DELETE(req, mockParams);
    const json = await res.json();
    expect(res.status).toBe(200);
    expect(json).toHaveProperty('success', true);
    expect(mockDelete).toHaveBeenCalledWith(expect.stringContaining('/admin/feeds/1'));
  });

  it('POST reparses a feed by ID', async () => {
    const req = {} as NextRequest;
    const res = await POST(req, mockParams);
    const json = await res.json();
    expect(res.status).toBe(200);
    expect(json).toHaveProperty('reparse', true);
    expect(mockPost).toHaveBeenCalledWith(expect.stringContaining('/admin/feeds/1/reparse'));
  });
});