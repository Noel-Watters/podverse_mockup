# backend/app/blueprints/feed/schemas.py

from app.extensions import ma
from app.models.feed import Feed, FeedFlagStatus, FeedLog
from datetime import datetime
from app.utils.error_exceptions import ValidationError

class FeedLogSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for serializing FeedLog objects.
    
    This schema excludes relationships and foreign keys to avoid circular references
    and provides a clean representation of feed parsing logs.
    """
    class Meta:
        model = FeedLog
        load_instance = True
        include_relationships = False
        include_fk = True


feed_log_schema = FeedLogSchema()
feed_logs_schema = FeedLogSchema(many=True)


class FeedFlagStatusSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for serializing FeedFlagStatus objects.
    
    This schema provides a clean representation of feed flag statuses
    without including relationships to avoid circular references.
    """
    class Meta:
        model = FeedFlagStatus
        load_instance = True
        include_relationships = False
        include_fk = True
        
feed_flag_status_schema = FeedFlagStatusSchema()
feed_flag_statuses_schema = FeedFlagStatusSchema(many=True)


class BaseFeedSchema(ma.SQLAlchemyAutoSchema):
    """
    Base schema for Feed objects with computed fields.
    
    This schema provides common computed fields that are used across
    different feed serialization contexts.
    """
    flag_status = ma.Method("get_flag_status")
    channel_title = ma.Method("get_channel_title")
    channel_podcast_index_id = ma.Method("get_channel_podcast_index_id")
    parsing_priority = ma.Method("suggest_priority_for_feed")

    class Meta:
        model = Feed
        load_instance = False
        include_fk = True

    def get_flag_status(self, feed_obj)->str:
        """
        Get the flag status string for a feed.
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            str: The flag status string, or None if no flag status exists
        """
        return feed_obj.flag_status.status if feed_obj.flag_status else None

    def get_channel_title(self, feed_obj)->str:
        """
        Get the channel title for a feed.
        
        This method handles multiple channels gracefully by returning the title
        of the first channel, or None if no channels exist. If multiple channels
        exist, it logs a warning but doesn't break the API response.
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            str: The channel title, or None if no channels exist
        """
        if not feed_obj.channels:
            return None
        if len(feed_obj.channels) > 1:
            # Log warning but don't break the API response
            import logging
            logging.warning(f"Feed {feed_obj.id} has multiple channels, using first one")
        return feed_obj.channels[0].title

    def get_channel_podcast_index_id(self, feed_obj)->int:
        """
        Get the podcast index ID for the first channel of a feed.
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            int: The podcast index ID, or None if no channels exist
        """
        return feed_obj.channels[0].podcast_index_id if feed_obj.channels else None
    
    def suggest_priority_for_feed(self, feed_obj) -> int:
        """
        Suggest parsing priority based on errors and last updated time.
        
        This method analyzes recent logs and update patterns to suggest
        an appropriate parsing priority for the feed.
        
        Priority levels:
        - 10: High priority (2+ recent errors)
        - 5: Medium priority (30+ days since update)
        - 1: Low priority (default)
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            int: Suggested parsing priority (1, 5, or 10)
        """
        if not feed_obj.logs:
            return 0
        recent_errors = sum(1 for log in feed_obj.logs[:3] if log.is_success is False)
        days_since_update = (datetime.utcnow() - feed_obj.updated_at).days

        if recent_errors >= 2:
            return 10  
        if days_since_update > 30:
            return 5   
        return 1       


class FeedSchema(BaseFeedSchema):
    """
    Schema for serializing individual Feed objects with recent logs.
    
    This schema includes recent logs and is used for detailed feed views
    where recent parsing history is relevant.
    """
    recent_logs = ma.Method("get_recent_logs")

    class Meta(BaseFeedSchema.Meta):
        fields = (
            "id", "url", "parsing_priority", "is_parsing", "created_at", "updated_at",
            "container_id", "last_parsed_file_hash", "flag_status", "channel_title",
            "channel_podcast_index_id", "recent_logs", "parsing_priority"
        )

    def get_recent_logs(self, feed_obj)->list[dict]:
        """
        Get the 2 most recent logs for a feed.
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            list[dict]: List of serialized recent log objects
        """
        sorted_logs = sorted(
            feed_obj.logs or [],
            key=lambda log: log.finished_at or datetime.min,
            reverse=True
        )
        return FeedLogSchema(many=True).dump(sorted_logs[:2])

feed_schema = FeedSchema()
feeds_schema = FeedSchema(many=True)

class FeedExportSchema(BaseFeedSchema):
    """
    Schema for serializing Feed objects for export operations.
    
    This schema includes additional computed fields that are useful for
    export operations, such as error counts and last successful parse times.
    """
    last_parse_error = ma.Method("get_last_parse_error")
    parse_error_count = ma.Method("get_parse_error_count")
    last_successful_parse_at = ma.Method("get_last_successful_parse_at")
    channel_issue = ma.Method("check_channel_issue")

    class Meta(BaseFeedSchema.Meta):
        fields = (
            'id', 'url', 'parsing_priority', 'is_parsing', 'created_at', 'updated_at',
            'flag_status', 'channel_title', 'channel_podcast_index_id',
            'last_parse_error', 'parse_error_count', 'last_successful_parse_at',
            'parsing_priority', 'channel_issue'
        )

    def get_last_parse_error(self, feed_obj)->str:
        """
        Get the most recent parse error message for a feed.
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            str: The last parse error message with timestamp, or None if no errors
        """
        if not feed_obj.logs:
            return None
        for log in sorted(feed_obj.logs, key=lambda log: log.finished_at or datetime.min, reverse=True):
            if log.is_success is False:
                return f"{log.parse_error_message} (at {log.finished_at})"
        return None

    def get_parse_error_count(self, feed_obj)->int:
        """
        Count the total number of parse errors for a feed.
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            int: The total number of parse errors
        """
        return sum(1 for log in feed_obj.logs if log.is_success is False)

    def get_last_successful_parse_at(self, feed_obj)->datetime:
        """
        Get the timestamp of the last successful parse for a feed.
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            datetime: The timestamp of the last successful parse, or None if no successful parses
        """
        successes = [log.finished_at for log in feed_obj.logs if log.is_success]
        return max(successes) if successes else None
    
    def check_channel_issue(self, feed_obj)->str:
        """
        Check for potential channel-related issues with a feed.
        
        Args:
            feed_obj (Feed): The feed object
            
        Returns:
            str: Description of the issue, or None if no issues found
        """
        if len(feed_obj.channels) > 1:
            return "Multiple channels linked"
        if not feed_obj.channels:
            return "No channel linked"
        return None

feed_export_schema = FeedExportSchema()
feeds_export_schema = FeedExportSchema(many=True)