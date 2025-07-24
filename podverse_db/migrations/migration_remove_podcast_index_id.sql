-- Migration: Remove podcast_index_id column from feed table
-- Run this script if your database still has the podcast_index_id column

ALTER TABLE feed DROP COLUMN IF EXISTS podcast_index_id; 