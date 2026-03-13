CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type VARCHAR(20) NOT NULL,
    raw_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL,
    findings JSONB NOT NULL,
    classification JSONB NOT NULL,
    triage JSONB NOT NULL,
    explainability JSONB NOT NULL,
    inconsistencies JSONB NOT NULL,
    lifestyle JSONB NOT NULL,
    follow_up JSONB NOT NULL,
    notification JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_report_results_report_id ON report_results(report_id);
