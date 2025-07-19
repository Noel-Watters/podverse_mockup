# tests/integration/blueprints/channel/test_channel_controller.py

import pytest
from flask import url_for
from app.models import Channel

# Import test configuration to override environment variables
import test_config

@pytest.fixture()
def add_sample_channel(session):
    # First create a feed since channel requires feed_id
    from app.models import Feed
    feed = Feed(url="http://example.com/test-feed.xml", feed_flag_status_id=1)
    session.add(feed)
    session.flush()  # Get the feed ID
    
    import uuid
    unique_id = str(uuid.uuid4())[:15]  # Use first 15 chars of UUID for id_text
    unique_podcast_index_id = int(uuid.uuid4().int % 1_000_000_000)  # large random int
    channel = Channel(
        id_text=unique_id,
        title=f"Sample Channel {unique_id}", 
        podcast_index_id=unique_podcast_index_id,
        feed_id=feed.id
    )
    session.add(channel)
    session.commit()
    return channel

def test_list_channels(test_client, add_sample_channel):
    response = test_client.get("/admin/channels")
    assert response.status_code == 200
    assert "Sample Channel" in response.get_data(as_text=True)

def test_get_channel_by_id(test_client, add_sample_channel):
    response = test_client.get(f"/admin/channels/{add_sample_channel.id}")
    assert response.status_code == 200
    assert add_sample_channel.title in response.get_data(as_text=True)

def test_get_channels_by_feed(test_client, add_sample_channel):
    feed_id = add_sample_channel.feed_id
    response = test_client.get(f"/admin/channels/by-feed?feed_ids={feed_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["meta"]["requested_feed_ids"] == [feed_id]
    assert data["meta"]["found_feed_ids"] == [feed_id]

def test_export_channels(test_client, add_sample_channel):
    response = test_client.get("/admin/channels/export")
    assert response.status_code == 200
    assert "text/csv" in response.headers["Content-Type"]
