from seed_utils import get_db_session, fake, unique_uuid
from app.models.item import Item
from app.models.channel import Channel
from app.models.item import ItemFlagStatus
from sqlalchemy.exc import IntegrityError
import random
import time
import string
from datetime import datetime

def generate_unique_id_text(session, max_attempts=10):
    """Generate a unique id_text that doesn't exist in the database"""
    for attempt in range(max_attempts):
        # Use timestamp + random string to ensure uniqueness
        timestamp = int(time.time() * 1000) % 1000000  # Last 6 digits of timestamp
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        id_text = f"{timestamp}{random_str}"
        
        # Check if this id_text already exists
        existing = session.query(Item).filter(Item.id_text == id_text).first()
        if not existing:
            return id_text
    
    # Fallback to UUID-based approach if timestamp method fails
    return f"item_{unique_uuid().hex[:16]}"

def seed_item(items_per_channel=1, additional_random_items=0):
    """
    Seed items for all channels
    
    Args:
        items_per_channel: Number of items to create for each channel (default: 1)
        additional_random_items: Additional random items to distribute across channels (default: 0)
    """
    session = get_db_session()
    try:
        channels = session.query(Channel).all()
        statuses = session.query(ItemFlagStatus).all()

        if not channels:
            print("⚠️  No channels found. Please seed channels first.")
            return
        if not statuses:
            print("⚠️  No item flag statuses found. Please seed item_flag_status first.")
            return

        print(f"📦 Seeding {items_per_channel} item(s) per channel + {additional_random_items} additional random items...")
        
        items = []
        successful_inserts = 0

        # Create items for each channel
        for channel in channels:
            for i in range(items_per_channel):
                try:
                    id_text = generate_unique_id_text(session)
                    status = random.choice(statuses)
                    
                    item = Item(
                        id_text=id_text,
                        slug=fake.slug(),
                        channel_id=channel.id,
                        guid=fake.uri(),
                        guid_enclosure_url=fake.url(),
                        pub_date=fake.date_time_between(start_date='-1y', end_date='now'),
                        title=fake.sentence(nb_words=6),
                        item_flag_status_id=status.id
                    )
                    items.append(item)
                    successful_inserts += 1
                    
                except Exception as e:
                    print(f"Error creating item for channel {channel.id}: {e}")
                    continue

        # Create additional random items
        for _ in range(additional_random_items):
            try:
                channel = random.choice(channels)
                id_text = generate_unique_id_text(session)
                status = random.choice(statuses)
                
                item = Item(
                    id_text=id_text,
                    slug=fake.slug(),
                    channel_id=channel.id,
                    guid=fake.uri(),
                    guid_enclosure_url=fake.url(),
                    pub_date=fake.date_time_between(start_date='-1y', end_date='now'),
                    title=fake.sentence(nb_words=6),
                    item_flag_status_id=status.id
                )
                items.append(item)
                successful_inserts += 1
                
            except Exception as e:
                print(f"Error creating additional random item: {e}")
                continue

        if items:
            session.add_all(items)
            session.commit()
            print(f"✅ Seeded {successful_inserts} items successfully")
            
            # Show statistics
            channels_with_items = session.query(Item.channel_id).distinct().count()
            total_channels = len(channels)
            print(f"📊 Statistics:")
            print(f"   - Total channels: {total_channels}")
            print(f"   - Channels with items: {channels_with_items}")
            print(f"   - Average items per channel: {successful_inserts / total_channels:.1f}")
        else:
            print("No items to seed")

    except IntegrityError as e:
        session.rollback()
        print("⚠️  Integrity error while inserting items:", str(e))
        # Try to identify which specific constraint was violated
        if "item_id_text_key" in str(e):
            print("   This suggests duplicate id_text values.")
        elif "item_slug" in str(e):
            print("   This suggests duplicate slug values.")
        elif "item_guid" in str(e):
            print("   This suggests duplicate guid values.")
    except Exception as e:
        session.rollback()
        print(f"❌ Unexpected error while seeding items: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    items_per_channel = 1
    additional_items = 0
    
    if len(sys.argv) > 1:
        try:
            items_per_channel = int(sys.argv[1])
        except ValueError:
            print("Invalid items_per_channel value. Using default: 1")
    
    if len(sys.argv) > 2:
        try:
            additional_items = int(sys.argv[2])
        except ValueError:
            print("Invalid additional_items value. Using default: 0")
    
    print(f"Seeding {items_per_channel} item(s) per channel + {additional_items} additional items")
    seed_item(items_per_channel, additional_items)
