-- Migration: Add podcast_index_id column to feeds table
-- Date: 2025-07-14

-- Add podcast_index_id column to feed table
ALTER TABLE feed ADD COLUMN IF NOT EXISTS podcast_index_id INTEGER;

COMMENT ON COLUMN feed.podcast_index_id IS 'Podcast Index ID for external podcast identification';
