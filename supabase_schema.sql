-- ============================================================================
-- Task Manager Agent - Complete Supabase Setup Script
-- ============================================================================
-- Instructions:
-- 1. Open your Supabase Dashboard: https://supabase.com/dashboard
-- 2. Select your new project
-- 3. Click "SQL Editor" in the left sidebar
-- 4. Click "New query"
-- 5. Paste this entire script and click "Run"
-- ============================================================================

-- 1. Create Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    due_date TIMESTAMP WITH TIME ZONE,
    estimated_hours FLOAT DEFAULT 0.0,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL DEFAULT gen_random_uuid(),
    assigned_to UUID
);

-- 2. Create Reminders Table
CREATE TABLE IF NOT EXISTS reminders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    reminder_time TIMESTAMP WITH TIME ZONE NOT NULL,
    notification_type VARCHAR(20) DEFAULT 'in_app',
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create Calendar Events Table (Optional integration)
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    calendar_id VARCHAR(255),
    event_id VARCHAR(255),
    title VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_created_by ON tasks(created_by);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reminders_task_id ON reminders(task_id);
CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status);
CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time) WHERE status = 'pending';

-- 5. Enable Row Level Security (RLS)
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;

-- 6. Set Permissive RLS Policies for API Access
DROP POLICY IF EXISTS "Allow all operations" ON tasks;
DROP POLICY IF EXISTS "Allow public access" ON tasks;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON tasks;
CREATE POLICY "Allow all operations" ON tasks
    FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all operations" ON reminders;
DROP POLICY IF EXISTS "Allow public access" ON reminders;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON reminders;
CREATE POLICY "Allow all operations" ON reminders
    FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all operations" ON calendar_events;
DROP POLICY IF EXISTS "Allow public access" ON calendar_events;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON calendar_events;
CREATE POLICY "Allow all operations" ON calendar_events
    FOR ALL USING (true) WITH CHECK (true);

-- 7. Verification: Confirm tables are created
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('tasks', 'reminders', 'calendar_events')
ORDER BY table_name, ordinal_position;
