import pytest

@pytest.mark.parametrize("endpoint", [
    "/stats/channels",
    "/stats/items",
    "/stats/channels/1",
    "/stats/items/1",
])

def test_stats_routes_exist(test_client, endpoint):
    response = test_client.get(endpoint)
    assert response.status_code in (200, 401, 403)
