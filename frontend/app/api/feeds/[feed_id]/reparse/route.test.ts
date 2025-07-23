

const mockPost = jest.fn().mockResolvedValue({ data: { reparse: true }, status: 200 });

jest.mock('axios', () => ({
  post: mockPost,
}));

import { POST } from './route';
import { NextRequest } from 'next/server';

jest.mock('@/lib/auth0', () => ({
  auth0: { getSession: jest.fn().mockResolvedValue({ accessToken: 'fake-token' }) }
}));

const mockParams = { params: { feed_id: '1' } };

describe('/api/feeds/[feed_id] API Route', () => {
  beforeEach(() => {
    jest.clearAllMocks();
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