import argparse
import inspect
from seed_utils import run_seeder_with_retry
from app.utils.request_logger import get_logger
from app import create_app

# Import all seeders
from seed_user import seed_user
from seed_feed_flag_status import seed_feed_flag_status
from seed_feed import seed_feed
from seed_channel import seed_channel
from seed_channel_category import seed_channel_category
from seed_item_flag_status import seed_item_flag_status
from seed_item import seed_item
from seed_sharable_status import seed_sharable_status
from seed_account import seed_account
from seed_stats_track_account_guid import seed_stats_track_account_guid
from seed_stats_event_channel import seed_stats_event_channel
from seed_stats_event_item import seed_stats_event_item
from seed_stats_aggregated_channel import seed_stats_aggregated_channel
from seed_stats_aggregated_item import seed_stats_aggregated_item
from seed_export_logs import seed_export_logs

# Seeder list (name, seeder function)
SEED_JOBS = [
    ("Users", seed_user),
    ("Feed Flag Status", seed_feed_flag_status),
    ("Feeds", seed_feed),
    ("Channels", seed_channel),
    ("Channel Categories", seed_channel_category),
    ("Item Flag Status", seed_item_flag_status),
    ("Items", seed_item),
    ("Sharable Status", seed_sharable_status),
    ("Accounts", seed_account),
    ("Account GUIDs", seed_stats_track_account_guid),
    ("Stats Event Channel", seed_stats_event_channel),
    ("Stats Event Item", seed_stats_event_item),
    ("Stats Aggregated Channel", seed_stats_aggregated_channel),
    ("Stats Aggregated Item", seed_stats_aggregated_item),
    ("Export Logs", seed_export_logs),
]

def normalize_name(name: str):
    return name.lower().replace(" ", "_")

def main():
    parser = argparse.ArgumentParser(description="Seed the Podverse database")
    parser.add_argument("--only", help="Comma-separated list of seeders to run (normalized names)", type=str)
    parser.add_argument("--skip", help="Comma-separated list of seeders to skip (normalized names)", type=str)
    parser.add_argument("--count", help="Override count for seeders that accept n", type=int, default=25)

    args = parser.parse_args()

    only = set(normalize_name(name) for name in args.only.split(",")) if args.only else None
    skip = set(normalize_name(name) for name in args.skip.split(",")) if args.skip else set()

    print("\n Starting full seeding process...\n")

    summary = []

    # Track Objects for passing
    feeds = []

    for label, func in SEED_JOBS:
        normalized = normalize_name(label)

        if only and normalized not in only:
            continue
        if normalized in skip:
            print(f"Skipping {label}")
            continue
        
        try:
            if normalized == "feeds":
                feed_ids = run_seeder_with_retry(lambda: func(n=100), label=label, return_result=True)
            elif normalized == "channels":
                run_seeder_with_retry(lambda: func(feed_ids), label=label)
            else:
                try:
                    sig = inspect.signature(func)
                    if "n" in sig.parameters:
                        run_seeder_with_retry(lambda: func(n=args.count), label=label)
                    else:
                        run_seeder_with_retry(func, label=label)
                except TypeError:
                    # For seeders that don't accept `n`
                    run_seeder_with_retry(func, label=label)
      
            summary.append(f"{label}")
        except Exception as e:
            print(f"Failed to run {label}: {e}")

    print("\n Seeder Summary:")
    for entry in summary:
        print(" ", entry)

    print("\n All seeders completed. Database is ready!\n")

if __name__ == "__main__":
    main()
