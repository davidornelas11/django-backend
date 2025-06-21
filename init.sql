-- Initialize the meal_planning database
-- This script runs when the PostgreSQL container starts for the first time

-- Create the database if it doesn't exist
-- (PostgreSQL creates it automatically based on POSTGRES_DB environment variable)

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE meal_planning TO postgres;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC'; 