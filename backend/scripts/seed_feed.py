from datetime import datetime, timedelta
from seed_utils import get_db_session, fake, unique_uuid
from app.models.feed import Feed, FeedLog, FeedFlagStatus
from sqlalchemy.exc import IntegrityError
import random

# Predefined realistic log scenarios
LOG_SCENARIOS = [
    {
        "status": 500,
        "errors": 1,
        "message": "Parsing failed: Malformed XML detected. Check for unclosed tags or invalid structure.",
    },
    {
        "status": 0,
        "errors": 1,
        "message": "Connection error: Unable to reach server. Verify feed URL or check firewall rules.",
    },
    {
        "status": 200,
        "errors": 0,
        "message": "Feed parsed successfully. All items updated with no issues.",
    },
    {
        "status": 404,
        "errors": 1,
        "message": "HTTP 404 Not Found: The requested RSS feed URL could not be located.",
    },
    {
        "status": 403,
        "errors": 1,
        "message": "Access Denied: HTTP 403 Forbidden. Server is blocking feed requests.",
    },
    {
        "status": 200,
        "errors": 0,
        "message": "Feed successfully parsed. 3 new items added, 1 item updated.",
    },
    {
        "status": 0,
        "errors": 1,
        "message": "Character Encoding Error: Unable to decode feed content using declared charset.",
    }
]

def seed_feed(n=100):
    session = get_db_session()
    feeds = []
    try:
        # Fetch actual feed_flag_status ids
        status_ids = [s.id for s in session.query(FeedFlagStatus).all()]
        if not status_ids:
            raise RuntimeError("No feed_flag_status values were found. These must be seeded first.")
        
        for _ in range(n):
            url = f"https://{fake.domain_name()}/{'-'.join(fake.words(nb=3))}-{str(unique_uuid())[:6]}/rss"
            feed = Feed(
                url=url,
                feed_flag_status_id=random.choice(status_ids),
                is_parsing=fake.boolean(chance_of_getting_true=10),
                parsing_priority=random.randint(0, 5),
                last_parsed_file_hash=fake.md5(),
                container_id=fake.bothify(text="##########"),
                created_at=datetime.utcnow() - timedelta(minutes=random.randint(11, 40)),
                updated_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 10))
            )
            session.add(feed)
            session.flush()  # So we can use feed.id before commit
            feeds.append(feed) # Save feed to list for channel use

            # Generate 1–3 log entries with useful diagnostic messages
            for _ in range(random.randint(1, 3)):
                scenario = random.choice(LOG_SCENARIOS)
                log = FeedLog(
                    feed_id=feed.id,
                    http_status=scenario["status"],
                    is_success=(scenario["status"] == 200),
                    parse_errors=scenario["errors"],
                    parse_error_message=scenario["message"],
                    started_at=datetime.utcnow() - timedelta(minutes=random.randint(6, 20)),
                    finished_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 5)),
                    parsed_by=random.choice(["auth0|admin1", "auth0|admin2", "auth0|admin3"])
                )
                session.add(log)
        
        session.flush()
        feed_ids = [feed.id for feed in feeds]
        print(feed_ids)
        session.commit()
        print(f"Seeded {n} feeds with diverse statuses and logs successfully")
        return feed_ids
        
    except IntegrityError as e:
        session.rollback()
        print("Integrity error while inserting feeds or logs:", str(e))
        return []
    finally:
        session.close()

if __name__ == "__main__":
    seed_feed()
# This script seeds the database with realistic feed data and logs.