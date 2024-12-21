-- Drop existing tables
DROP TABLE IF EXISTS deployment CASCADE;
DROP TABLE IF EXISTS cluster CASCADE;
DROP TABLE IF EXISTS organization CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

-- Recreate tables (this will be handled by SQLAlchemy) 