# Testing Get All Stat Endpoints Exist
import pytest
from unittest.mock import patch

@pytest.mark.parametrize("endpoint, service", [
    ("/admin/stats/channels", "app.blueprints.stats.routes.list_channel_stats"),
    ("/admin/stats/items", "app.blueprints.stats.routes.list_item_stats"),
])


def test_stats_routes_exist(test_client, endpoint, service):
    with patch(service) as mock_service:
        mock_service.return_value = {
            "results": [],
            "page": 1,
            "per_page": 10,
            "total": 0,
            "view": "monthly"
        }
        response = test_client.get(endpoint)
        assert response.status_code in (200, 401, 403)
