-- Flowstate-AI Seed Data
-- Sample data for development and testing

-- Insert sample user
INSERT INTO users (id, email, name, role) 
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'admin@flowstate.ai', 'Admin User', 'admin'),
    ('00000000-0000-0000-0000-000000000002', 'demo@flowstate.ai', 'Demo User', 'user')
ON CONFLICT (email) DO NOTHING;

-- Insert sample customers
INSERT INTO customers (id, user_id, name, email, phone, pipeline_stage, relationship_score, notes)
VALUES
    (uuid_generate_v4(), '00000000-0000-0000-0000-000000000002', 'John Smith', 'john.smith@example.com', '+1-555-0101', 'qualified', 75, 'Interested in premium package'),
    (uuid_generate_v4(), '00000000-0000-0000-0000-000000000002', 'Sarah Johnson', 'sarah.j@example.com', '+1-555-0102', 'contacted', 60, 'Follow up next week'),
    (uuid_generate_v4(), '00000000-0000-0000-0000-000000000002', 'Mike Davis', 'mike.d@example.com', '+1-555-0103', 'new', 50, 'New lead from website'),
    (uuid_generate_v4(), '00000000-0000-0000-0000-000000000002', 'Emily Chen', 'emily.chen@example.com', '+1-555-0104', 'proposal_sent', 85, 'Proposal sent, awaiting response'),
    (uuid_generate_v4(), '00000000-0000-0000-0000-000000000002', 'David Wilson', 'david.w@example.com', '+1-555-0105', 'customer', 95, 'Active customer, very satisfied')
ON CONFLICT DO NOTHING;

-- Log seed completion
DO $$
BEGIN
    RAISE NOTICE 'Seed data loaded successfully at %', NOW();
END $$;

