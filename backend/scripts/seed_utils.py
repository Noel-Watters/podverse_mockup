# backend/scripts/seed_utils.py
from datetime import datetime, timedelta
import random
from uuid import uuid4
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
import uuid
from app.extensions import db
from app.utils.request_logger import get_logger

# Initialize Faker
fake = Faker()

# Setup database connection
if not os.getenv("DATABASE_URL"):
    raise ValueError("DATABASE_URL environment variable is required")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Provides a new database session."""
    return SessionLocal()

def random_past_date(within_days=365):
    return datetime.utcnow() - timedelta(
        days=random.randint(0, within_days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

def random_device_info():
    devices = [
        "iPhone 14, iOS 16.4",
        "Samsung Galaxy S22, Android 13",
        "Chrome on Windows 10",
        "Firefox on macOS",
        "Safari on iPadOS",
        "Edge on Windows 11",
        "Android Tablet",
        "Linux Desktop",
    ]
    return random.choice(devices)

def random_location():
    countries = [
        "USA",
        "Canada",
        "UK",
        "Australia",
        "Germany",
        "France",
        "India",
        "Brazil",
    ]
    return random.choice(countries)

def unique_uuid():
    """Returns a proper UUID object for database storage"""
    return uuid.uuid4()

def unique_uuid_str():
    """Returns a UUID as string for cases that need string representation"""
    return str(uuid.uuid4())

def clear_existing_channels():
    """Safely clear existing channel data to prevent duplicate key violations"""
    session = get_db_session()
    try:
        from app.models.channel import Channel
        count = session.query(Channel).count()
        if count > 0:
            print(f"Found {count} existing channels. Clearing...")
            session.query(Channel).delete()
            session.commit()
            print("✅ Existing channels cleared successfully")
        else:
            print("No existing channels found")
        return True
    except Exception as e:
        session.rollback()
        print(f"❌ Error clearing channels: {e}")
        return False
    finally:
        session.close()

def check_existing_data(model_class, label=""):
    """Check if data already exists for a given model"""
    session = get_db_session()
    try:
        count = session.query(model_class).count()
        if count > 0:
            print(f"⚠️  Found {count} existing {label or model_class.__name__} records")
            return True
        else:
            print(f"✅ No existing {label or model_class.__name__} records found")
            return False
    except Exception as e:
        print(f"❌ Error checking existing {label or model_class.__name__}: {e}")
        return False
    finally:
        session.close()

import time
import traceback

def run_seeder_with_retry(seeder_func, label="", retries=3, delay=3, return_result=False):
    attempt = 0
    while attempt < retries:
        try:
            print(f"Seeding {label} (Attempt {attempt + 1}/{retries})...")
            result = seeder_func()
            print(f"{label} seeded successfully!\n")
            return result if return_result else None
        except Exception as e:
            print(f"Error seeding {label}: {e}")
            traceback.print_exc()
            attempt += 1
            time.sleep(delay)
    print(f"Failed to seed {label} after {retries} attempts.\n")
