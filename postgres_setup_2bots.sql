-- PostgreSQL setup for 2 bots in 6x6x6 grid
-- Position bots at top right corner: (5,5,1) and (5,5,4)

-- Add new columns for real-time tracking
ALTER TABLE bots ADD COLUMN IF NOT EXISTS assigned_order_id INTEGER;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS destination_bin JSONB;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS path JSONB;

-- Update existing bots to have default status
UPDATE bots SET status = 'idle' WHERE status IS NULL;

-- Clear existing bots and add 2 bots at top right corner
DELETE FROM bots;

-- Insert 2 bots at top right corner of 6x6x6 grid
INSERT INTO bots (id, x, y, current_location_z, status) VALUES
(1, 5, 5, 1, 'idle'),  -- Bot 1 at (5,5,1)
(2, 5, 5, 4, 'idle');  -- Bot 2 at (5,5,4)

-- Set default values for new columns
UPDATE bots SET 
    assigned_order_id = NULL,
    destination_bin = NULL,
    path = NULL
WHERE assigned_order_id IS NULL;

-- Show the updated table structure
\d bots

-- Show current bots
SELECT id, x, y, current_location_z, status, assigned_order_id, destination_bin, path FROM bots; 