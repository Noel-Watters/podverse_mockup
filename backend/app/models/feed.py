# backend/app/models/feed.py
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.extensions import db
from app.models.base import Base
from sqlalchemy.orm import relationship

class Feed(Base):
    __tablename__ = "feed"

    id: Mapped[int] = mapped_column(primary_key=True)
    feed_flag_status_id: Mapped[int] = mapped_column(db.ForeignKey("feed_flag_status.id"))
    url: Mapped[str] = mapped_column(String(2083), unique=True)
    last_parsed_file_hash: Mapped[Optional[str]] = mapped_column(String(32))
    parsing_priority: Mapped[int] = mapped_column(Integer, default=0)
    container_id: Mapped[Optional[str]] = mapped_column(String(12))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=db.func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=db.func.now(), onupdate=db.func.now())
    is_parsing: Mapped[Optional[bool]] = mapped_column(db.Boolean)

    flag_status = relationship("FeedFlagStatus", back_populates="feeds")
    channels = relationship("Channel", back_populates="feed")
    logs = relationship(
        "FeedLog",
        back_populates="feed",
        cascade="all, delete-orphan",
        order_by="desc(FeedLog.finished_at)"
    )

    @property
    def recent_logs(self):
        return self.logs[:2]  # adjust count as needed

class FeedFlagStatus(Base):
    __tablename__ = "feed_flag_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=db.func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=db.func.now(), onupdate=db.func.now())
    status: Mapped[str] = mapped_column(String(50))

    feeds = relationship("Feed", back_populates="flag_status")

class FeedLog(Base):
    __tablename__ = "feed_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    feed_id: Mapped[int] = mapped_column(db.ForeignKey("feed.id"))
    http_status: Mapped[Optional[int]] = mapped_column(db.Integer) # HTTP status based on result of parse
    is_success: Mapped[Optional[bool]] = mapped_column(db.Boolean) # T or F based on the Reparse Result
    parse_errors: Mapped[Optional[int]] = mapped_column(db.Integer, default=0)
    parse_error_message: Mapped[Optional[str]] = mapped_column(String(255)) # new field to hold message
    started_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    finished_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    parsed_by: Mapped[Optional[str]] = mapped_column(String(255)) # This will come as an Auth0 ID

    feed = relationship("Feed", back_populates="logs")
