-- V10: Add tables for background jobs and notifications

-- Sync metrics aggregation table
CREATE TABLE IF NOT EXISTS sync_metrics_hourly (
    id SERIAL PRIMARY KEY,
    period_start TIMESTAMP NOT NULL UNIQUE,
    total_operations INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    conflict_count INTEGER NOT NULL DEFAULT 0,
    unique_devices INTEGER NOT NULL DEFAULT 0,
    avg_processing_ms DECIMAL(10, 2),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sync_metrics_period ON sync_metrics_hourly (period_start DESC);

-- Weekly reports table
CREATE TABLE IF NOT EXISTS weekly_reports (
    id SERIAL PRIMARY KEY,
    week_start TIMESTAMP NOT NULL,
    report_data JSONB NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_weekly_reports_week ON weekly_reports (week_start DESC);

-- Usuario device table (for push notifications)
CREATE TABLE IF NOT EXISTS usuario_device (
    id SERIAL PRIMARY KEY,
    usuario_id VARCHAR(255) NOT NULL,
    device_id VARCHAR(255) NOT NULL UNIQUE,
    fcm_token TEXT,
    device_type VARCHAR(50),  -- android, ios, web
    device_model VARCHAR(255),
    os_version VARCHAR(50),
    app_version VARCHAR(50),
    active BOOLEAN NOT NULL DEFAULT true,
    last_seen TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usuario_device_usuario ON usuario_device (usuario_id);
CREATE INDEX IF NOT EXISTS idx_usuario_device_active ON usuario_device (active) WHERE active = true;

-- Trigger for updated_at
CREATE TRIGGER update_usuario_device_updated_at
    BEFORE UPDATE ON usuario_device
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Usuario papel table (for role-based notifications)
CREATE TABLE IF NOT EXISTS usuario_papel (
    usuario_id VARCHAR(255) NOT NULL,
    papel papel NOT NULL,
    PRIMARY KEY (usuario_id, papel),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usuario_papel_papel ON usuario_papel (papel);

-- Add comments
COMMENT ON TABLE sync_metrics_hourly IS 'Hourly aggregated sync metrics for monitoring';
COMMENT ON TABLE weekly_reports IS 'Weekly automated reports';
COMMENT ON TABLE usuario_device IS 'User devices for push notifications';
COMMENT ON TABLE usuario_papel IS 'User roles for RBAC and notifications';

-- Sample data for testing
INSERT INTO usuario_papel (usuario_id, papel) VALUES
    ('sistema', 'ADMIN'),
    ('gestor01', 'GESTOR'),
    ('agente01', 'CAMPO')
ON CONFLICT DO NOTHING;
