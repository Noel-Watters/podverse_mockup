

const mockGet = jest.fn().mockResolvedValue({ data: { id: 1, title: 'Feed 1' }, status: 200 });
const mockPut = jest.fn().mockResolvedValue({ data: { id: 1, title: 'Updated Feed' }, status: 200 });
const mockDelete = jest.fn().mockResolvedValue({ data: { success: true }, status: 200 });

jest.mock('axios', () => ({
  get: mockGet,
  put: mockPut,
  delete: mockDelete,

}));

import { GET} from './route';
import { NextRequest } from 'next/server';

jest.mock('@/lib/auth0', () => ({
  auth0: { getSession: jest.fn().mockResolvedValue({ accessToken: 'fake-token' }) }
}));

const mockParams = { params: { feed_id: '1' } };

describe('/api/channels/[feed_id] API Route', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('GET returns a channel by ID', async () => {
    const req = {} as NextRequest;
    const res = await GET(req);
    const json = await res.json();
    expect(res.status).toBe(200);
    expect(json).toHaveProperty('id', 1);
    expect(json).toHaveProperty('title', 'Feed 1');
    expect(mockGet).toHaveBeenCalledWith(expect.stringContaining('/admin/channels/1'));
  });
});
