-- Migration: Create Evolution Framework Tables
-- Created: 2025-10-12
-- Description: Creates tables for the Evolution Framework to track self-improvement activities

-- Evolution events table
CREATE TABLE IF NOT EXISTS evolution_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    type VARCHAR(50) NOT NULL CHECK (type IN ('code_modification', 'parameter_tuning', 'knowledge_acquisition', 'anomaly_response')),
    component VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    proposed_by VARCHAR(50) NOT NULL CHECK (proposed_by IN ('evolution_manager', 'self_modification_orchestrator', 'anomaly_detector', 'human')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('proposed', 'validated', 'applied', 'rolled_back', 'rejected')),
    metrics_before JSONB,
    metrics_after JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(100) NOT NULL,
    value NUMERIC NOT NULL,
    unit VARCHAR(20),
    component VARCHAR(100) NOT NULL,
    context JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Anomaly reports table
CREATE TABLE IF NOT EXISTS anomaly_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT NOT NULL,
    detected_value NUMERIC NOT NULL,
    expected_min NUMERIC,
    expected_max NUMERIC,
    z_score NUMERIC,
    resolution TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Evolution configuration table
CREATE TABLE IF NOT EXISTS evolution_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_evolution_events_timestamp ON evolution_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_evolution_events_type ON evolution_events(type);
CREATE INDEX IF NOT EXISTS idx_evolution_events_status ON evolution_events(status);
CREATE INDEX IF NOT EXISTS idx_evolution_events_component ON evolution_events(component);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_component ON performance_metrics(component);

CREATE INDEX IF NOT EXISTS idx_anomaly_reports_timestamp ON anomaly_reports(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_reports_severity ON anomaly_reports(severity);
CREATE INDEX IF NOT EXISTS idx_anomaly_reports_resolved ON anomaly_reports(resolved_at);

-- Insert default evolution configuration
INSERT INTO evolution_config (key, value, description) VALUES
('enabled', 'true'::jsonb, 'Master switch for evolution framework'),
('safe_mode', 'false'::jsonb, 'Safe mode status - when true, automatic modifications are paused'),
('auto_apply_threshold', '0.8'::jsonb, 'Confidence threshold for automatic application of changes'),
('anomaly_threshold', '2.0'::jsonb, 'Z-score threshold for anomaly detection'),
('metrics_window', '100'::jsonb, 'Number of data points for statistical analysis'),
('knowledge_retention_days', '365'::jsonb, 'Days to retain knowledge entries'),
('cost_budget_daily_limit', '10.0'::jsonb, 'Daily cost limit in USD'),
('cost_budget_per_operation_limit', '0.50'::jsonb, 'Per-operation cost limit in USD')
ON CONFLICT (key) DO NOTHING;

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_evolution_events_updated_at BEFORE UPDATE ON evolution_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_evolution_config_updated_at BEFORE UPDATE ON evolution_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE evolution_events IS 'Tracks all evolutionary changes made by the system';
COMMENT ON TABLE performance_metrics IS 'Stores performance metrics for analysis and anomaly detection';
COMMENT ON TABLE anomaly_reports IS 'Records detected anomalies and their resolutions';
COMMENT ON TABLE evolution_config IS 'System-wide configuration for evolution behavior';
