from seed_utils import get_db_session
from app.models.channel import ChannelCategory
from app.models.channel import Channel
from app.models.category import Category
from sqlalchemy.exc import IntegrityError
import random

def seed_channel_category():
    """
    Seed channel-category associations.
    Each channel will be assigned 1-3 random categories.
    """
    session = get_db_session()
    try:
        # Get all channels and categories
        channels = session.query(Channel).all()
        categories = session.query(Category).all()
        
        if not channels:
            print("No channels found. Please seed channels first.")
            return
            
        if not categories:
            print("No categories found. Please seed categories first.")
            return
        
        # Clear existing associations )
        session.query(ChannelCategory).delete()
        session.commit()
        print("Cleared existing channel-category associations.")
        
        associations_created = 0
        
        for channel in channels:
            # Assign 1-3 random categories to each channel
            num_categories = random.randint(1, 3)
            selected_categories = random.sample(categories, min(num_categories, len(categories)))
            
            for category in selected_categories:
                # Check if association already exists
                existing = session.query(ChannelCategory).filter_by(
                    channel_id=channel.id,
                    category_id=category.id
                ).first()
                
                if not existing:
                    association = ChannelCategory(
                        channel_id=channel.id,
                        category_id=category.id
                    )
                    session.add(association)
                    associations_created += 1
        
        session.commit()
        print(f"✅ Successfully created {associations_created} channel-category associations")
        
        # Show some statistics
        total_channels = len(channels)
        total_categories = len(categories)
        channels_with_categories = session.query(ChannelCategory.channel_id).distinct().count()
        
        print(f"📊 Statistics:")
        print(f"   - Total channels: {total_channels}")
        print(f"   - Total categories: {total_categories}")
        print(f"   - Channels with categories: {channels_with_categories}")
        print(f"   - Average categories per channel: {associations_created / total_channels:.1f}")
        
    except IntegrityError as e:
        session.rollback()
        print(f"⚠️  Integrity error while creating channel-category associations: {str(e)}")
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating channel-category associations: {str(e)}")
    finally:
        session.close()

def seed_channel_category_specific(channel_ids=None, category_ids=None):
    """
    Seed specific channel-category associations.
    
    Args:
        channel_ids: List of channel IDs to assign categories to (if None, uses all channels)
        category_ids: List of category IDs to assign (if None, uses all categories)
    """
    session = get_db_session()
    try:
        # Get channels and categories based on provided IDs
        if channel_ids:
            channels = session.query(Channel).filter(Channel.id.in_(channel_ids)).all()
        else:
            channels = session.query(Channel).all()
            
        if category_ids:
            categories = session.query(Category).filter(Category.id.in_(category_ids)).all()
        else:
            categories = session.query(Category).all()
        
        if not channels:
            print("No channels found matching the provided IDs.")
            return
            
        if not categories:
            print("No categories found matching the provided IDs.")
            return
        
        associations_created = 0
        
        for channel in channels:
            # Assign 1-2 random categories from the specified list
            num_categories = random.randint(1, min(2, len(categories)))
            selected_categories = random.sample(categories, num_categories)
            
            for category in selected_categories:
                # Check if association already exists
                existing = session.query(ChannelCategory).filter_by(
                    channel_id=channel.id,
                    category_id=category.id
                ).first()
                
                if not existing:
                    association = ChannelCategory(
                        channel_id=channel.id,
                        category_id=category.id
                    )
                    session.add(association)
                    associations_created += 1
        
        session.commit()
        print(f"✅ Successfully created {associations_created} specific channel-category associations")
        
    except IntegrityError as e:
        session.rollback()
        print(f"⚠️  Integrity error: {str(e)}")
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    # Seed all channels with random categories
    seed_channel_category()
    
    # Or seed specific channels with specific categories
    # seed_channel_category_specific(channel_ids=[1, 2, 3], category_ids=[1, 2, 3, 4]) 