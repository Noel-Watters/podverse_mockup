#!/usr/bin/env python3
"""
Comprehensive seeding script for Podverse database
Handles all seeding operations with proper error handling and duplicate prevention
"""

import sys
import os
from seed_utils import run_seeder_with_retry, check_existing_data, clear_existing_channels

def print_database_stats():
    """Print current database statistics"""
    try:
        import sys
        sys.path.append('/app')
        from app.models.channel import Channel
        from app.models.item import Item
        from app.models.feed import Feed, FeedFlagStatus
        from app.extensions import db
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        import os

        # Setup database connection
        DATABASE_URL = os.getenv('DATABASE_URL')
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()

        # Check channel counts
        total_channels = session.query(Channel).count()
        channels_with_items = session.query(Channel).join(Item).distinct().count()
        channels_with_categories = session.query(Channel).join(Channel.categories).distinct().count()
        channels_with_mediums = session.query(Channel).filter(Channel.medium_id.isnot(None)).count()

        # Check feed counts
        total_feeds = session.query(Feed).count()
        feeds_with_channels = session.query(Feed).join(Feed.channels).distinct().count()

        # Check item counts
        total_items = session.query(Item).count()

        print(f'\n📊 Database Statistics:')
        print(f'   Total channels: {total_channels}')
        print(f'   Channels with items: {channels_with_items}')
        print(f'   Channels with categories: {channels_with_categories}')
        print(f'   Channels with mediums: {channels_with_mediums}')
        print(f'   Total items: {total_items}')
        print(f'   Total feeds: {total_feeds}')
        print(f'   Feeds with channels: {feeds_with_channels}')
        print(f'   Feeds without channels: {total_feeds - feeds_with_channels}')

        # Check if all channels have the required relationships
        all_channels_have_items = total_channels == channels_with_items
        all_channels_have_categories = total_channels == channels_with_categories
        all_channels_have_mediums = total_channels == channels_with_mediums

        print(f'\n✅ Relationship Status:')
        print(f'   All channels have items: {all_channels_have_items}')
        print(f'   All channels have categories: {all_channels_have_categories}')
        print(f'   All channels have mediums: {all_channels_have_mediums}')

        session.close()
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")

def main():
    print("Podverse Database Seeding Script")
    print("=" * 50)
    
    # Check command line arguments
    clear_existing = "--clear" in sys.argv
    force_seed = "--force" in sys.argv
    items_per_channel = 2  # Default: 2 items per channel
    additional_items = 50  # Default: 50 additional random items
    
    # Parse custom item counts if provided
    if "--items-per-channel" in sys.argv:
        try:
            idx = sys.argv.index("--items-per-channel")
            if idx + 1 < len(sys.argv):
                items_per_channel = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            pass
    
    if "--additional-items" in sys.argv:
        try:
            idx = sys.argv.index("--additional-items")
            if idx + 1 < len(sys.argv):
                additional_items = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            pass
    
    if clear_existing:
        print("🗑️  Clear mode enabled - will clear existing data before seeding")
    
    if force_seed:
        print("⚡ Force mode enabled - will seed even if data exists")
    
    print(f"Item seeding: {items_per_channel} per channel + {additional_items} additional")
    print()
    
    # Import seeding functions
    try:
        from seed_category import seed_category
        from seed_medium import seed_medium
        from seed_feed_flag_status import seed_feed_flag_status
        from seed_item_flag_status import seed_item_flag_status
        from seed_sharable_status import seed_sharable_status
        from seed_feed import seed_feed
        from seed_channel import seed_channel
        from seed_channel_category import seed_channel_category
        from seed_item import seed_item
        from seed_account import seed_account
        from seed_stats_track_account_guid import seed_stats_track_account_guid
        from seed_stats_event_channel import seed_stats_event_channel
        from seed_stats_aggregated_channel import seed_stats_aggregated_channel
        from seed_stats_event_item import seed_stats_event_item
        from seed_stats_aggregated_item import seed_stats_aggregated_item
        from seed_export_logs import seed_export_logs
    except ImportError as e:
        print(f"❌ Error importing seeding modules: {e}")
        print("Make sure all seeding scripts are in the same directory")
        return
    
    # Check for existing data
    if not clear_existing and not force_seed:
        print("🔍 Checking for existing data...")
        from app.models.channel import Channel
        from app.models.feed import Feed
        from app.models.item import Item
        
        has_channels = check_existing_data(Channel, "channels")
        has_feeds = check_existing_data(Feed, "feeds")
        has_items = check_existing_data(Item, "items")
        
        if has_channels or has_feeds or has_items:
            print("\n⚠️  Existing data found!")
            print("Use --clear to clear existing data before seeding")
            print("Use --force to seed anyway (may cause duplicate key violations)")
            print("\nExample: python seed_all.py --clear")
            return
    
    print("Starting seeding process...\n")
    
    # Seed in dependency order
    seeders = [
        ("Categories", lambda: seed_category()),
        ("Mediums", lambda: seed_medium()),
        ("Feed Flag Status", lambda: seed_feed_flag_status()),
        ("Item Flag Status", lambda: seed_item_flag_status()),
        ("Sharable Status", lambda: seed_sharable_status()),
    ]
    
    # Run basic seeders
    for label, seeder_func in seeders:
        run_seeder_with_retry(seeder_func, label)
    
    # Seed feeds (returns feed IDs needed for channels)
    print("Seeding feeds...")
    try:
        feed_ids = seed_feed(n=100)
        print(f"✅ Seeded {len(feed_ids)} feeds successfully\n")
    except Exception as e:
        print(f"❌ Error seeding feeds: {e}")
        return
    
    # Seed channels with clear option
    print("Seeding channels...")
    try:
        seed_channel(feed_ids, clear_existing=clear_existing)
        print()
    except Exception as e:
        print(f"❌ Error seeding channels: {e}")
        return
    
    # Seed channel categories (ensure all channels have categories)
    print("Seeding channel categories...")
    try:
        seed_channel_category()
        print()
    except Exception as e:
        print(f"❌ Error seeding channel categories: {e}")
        return
    
    # Seed items (ensure all channels have items)
    print("Seeding items...")
    try:
        seed_item(items_per_channel, additional_items)
        print()
    except Exception as e:
        print(f"❌ Error seeding items: {e}")
        return
    
    # Continue with remaining seeders
    remaining_seeders = [
        ("Accounts", lambda: seed_account()),
        ("Stats Track Account GUID", lambda: seed_stats_track_account_guid()),
        ("Stats Event Channel", lambda: seed_stats_event_channel()),
        ("Stats Aggregated Channel", lambda: seed_stats_aggregated_channel()),
        ("Stats Event Item", lambda: seed_stats_event_item()),
        ("Stats Aggregated Item", lambda: seed_stats_aggregated_item()),
        ("Export Logs", lambda: seed_export_logs()),
    ]
    
    for label, seeder_func in remaining_seeders:
        run_seeder_with_retry(seeder_func, label)
    
    # Print final statistics
    print_database_stats()
    
    print("\nSeeding completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
