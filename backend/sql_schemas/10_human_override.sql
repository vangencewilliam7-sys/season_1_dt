-- =============================================================================
-- 10_human_override.sql
-- Add sender classification and fix ID constraints for Human Override
-- =============================================================================

-- Add 'sender' column to track who actually sent the message
-- Values: 'twin', 'human_expert', 'user'
ALTER TABLE IF EXISTS chat_audit_logs
ADD COLUMN IF NOT EXISTS sender text DEFAULT 'twin';

-- Fix ID constraint where chat_audit_logs does not auto-generate a UUID
ALTER TABLE IF EXISTS chat_audit_logs
ALTER COLUMN id SET DEFAULT gen_random_uuid();
