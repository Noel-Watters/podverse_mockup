from seed_utils import get_db_session, fake, unique_uuid, clear_existing_channels, check_existing_data
from app.models.channel import Channel
from app.models.feed import Feed
from app.models.medium import Medium
from sqlalchemy.exc import IntegrityError
import random
import time
import string

def generate_unique_id_text(session, max_attempts=10):
    """Generate a unique id_text that doesn't exist in the database"""
    for attempt in range(max_attempts):
        # Use timestamp + random string to ensure uniqueness
        timestamp = int(time.time() * 1000) % 1000000  # Last 6 digits of timestamp
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        id_text = f"{timestamp}{random_str}"
        
        # Check if this id_text already exists
        existing = session.query(Channel).filter(Channel.id_text == id_text).first()
        if not existing:
            return id_text
    
    # Fallback to UUID-based approach if timestamp method fails
    return f"ch_{unique_uuid().hex[:16]}"

def generate_unique_podcast_index_id(session, max_attempts=10):
    """Generate a unique podcast_index_id that doesn't exist in the database"""
    for attempt in range(max_attempts):
        # Generate a random podcast_index_id in a reasonable range
        podcast_index_id = random.randint(1000, 99999)
        
        # Check if this podcast_index_id already exists
        existing = session.query(Channel).filter(Channel.podcast_index_id == podcast_index_id).first()
        if not existing:
            return podcast_index_id
    
    # Fallback to timestamp-based approach if random method fails
    return int(time.time() * 1000) % 100000

def seed_channel(feed_ids, clear_existing=False):
    """
    Seed channels for the given feed IDs
    
    Args:
        feed_ids: List of feed IDs to create channels for
        clear_existing: If True, clear existing channels before seeding
    """
    session = get_db_session()
    try:
        if not feed_ids:
            print("No feeds found. Please seed feeds first.")
            return

        # Check for existing channels
        has_existing = check_existing_data(Channel, "channels")
        
        if has_existing and clear_existing:
            if not clear_existing_channels():
                print("❌ Failed to clear existing channels. Aborting seeding.")
                return
        elif has_existing and not clear_existing:
            print("⚠️  Existing channels found. Use clear_existing=True to clear them first.")
            print("   Proceeding with seeding (may cause duplicate key violations)...")

        # Get medium ids
        mediums = session.query(Medium).all()
        medium_ids = [m.id for m in mediums]

        channels = []
        successful_inserts = 0
        skipped_count = 0

        for feed_id in feed_ids:
            try:
                # Generate unique id_text and podcast_index_id
                id_text = generate_unique_id_text(session)
                podcast_index_id = generate_unique_podcast_index_id(session)
                
                # Check if this feed_id already has a channel
                existing_channel = session.query(Channel).filter(Channel.feed_id == feed_id).first()
                if existing_channel:
                    print(f"Channel already exists for feed_id {feed_id}, skipping...")
                    skipped_count += 1
                    continue

                channel = Channel(
                    id_text=id_text,
                    slug=fake.slug(),
                    feed_id=feed_id,
                    podcast_index_id=podcast_index_id,
                    podcast_guid=unique_uuid(),
                    title=fake.sentence(nb_words=3),
                    sortable_title=fake.word().lower(),
                    medium_id=random.choice(medium_ids) if medium_ids else 1, #default to podcast if issue with getting medium_id
                    has_podcast_index_value=fake.boolean(chance_of_getting_true=30),
                    has_value_time_splits=fake.boolean(chance_of_getting_true=20)
                )
                channels.append(channel)
                successful_inserts += 1

            except Exception as e:
                print(f"Error creating channel for feed_id {feed_id}: {e}")
                continue

        if channels:
            session.add_all(channels)
            session.commit()
            print(f"✅ Seeded {successful_inserts} channels successfully")
            if skipped_count > 0:
                print(f"   Skipped {skipped_count} feeds that already had channels")
        else:
            print("No new channels to seed")

    except IntegrityError as e:
        session.rollback()
        print("⚠️  Integrity error while inserting channels:", str(e))
        # Try to identify which specific constraint was violated
        if "channel_id_text_key" in str(e):
            print("   This suggests duplicate id_text values. Consider clearing existing data or using a different seeding strategy.")
        elif "channel_podcast_guid_unique" in str(e):
            print("   This suggests duplicate podcast_guid values.")
        elif "channel_slug" in str(e):
            print("   This suggests duplicate slug values.")
        elif "channel_podcast_index_id_key" in str(e):
            print("   This suggests duplicate podcast_index_id values.")
        elif "channel_title_key" in str(e):
            print("   This suggests duplicate title values.")
        elif "channel_sortable_title_key" in str(e):
            print("   This suggests duplicate sortable_title values.")
    except Exception as e:
        session.rollback()
        print(f"❌ Unexpected error while seeding channels: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    import sys
    
    # Check if user wants to clear existing data
    clear_existing = False
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_existing = True
        print("🗑️  Will clear existing channels before seeding")
    
    from seed_feed import seed_feed
    feeds = seed_feed(n=100)
    seed_channel(feeds, clear_existing=clear_existing)