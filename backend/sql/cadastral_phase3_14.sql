CREATE EXTENSION IF NOT EXISTS postgis;

ALTER TABLE cadastral_layers
    ADD COLUMN IF NOT EXISTS import_warnings JSONB;

ALTER TABLE old_parcels
    ADD COLUMN IF NOT EXISTS attributes JSONB;

ALTER TABLE old_parcels
    ADD COLUMN IF NOT EXISTS validation_status VARCHAR(30)
    DEFAULT 'VALID';

ALTER TABLE old_parcels
    ADD COLUMN IF NOT EXISTS validation_message TEXT;

ALTER TABLE old_parcels
    ADD COLUMN IF NOT EXISTS local_crs VARCHAR(100);

ALTER TABLE new_parcels
    ADD COLUMN IF NOT EXISTS attributes JSONB;

ALTER TABLE new_parcels
    ADD COLUMN IF NOT EXISTS validation_status VARCHAR(30)
    DEFAULT 'VALID';

ALTER TABLE new_parcels
    ADD COLUMN IF NOT EXISTS validation_message TEXT;

ALTER TABLE new_parcels
    ADD COLUMN IF NOT EXISTS local_crs VARCHAR(100);

CREATE TABLE IF NOT EXISTS comparison_runs (
    id UUID PRIMARY KEY,
    old_layer_id UUID NOT NULL REFERENCES cadastral_layers(id),
    new_layer_id UUID NOT NULL REFERENCES cadastral_layers(id),
    survey_id UUID NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',
    thresholds JSONB,
    summary JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comparison_runs_old_layer
ON comparison_runs(old_layer_id);

CREATE INDEX IF NOT EXISTS idx_comparison_runs_new_layer
ON comparison_runs(new_layer_id);

CREATE TABLE IF NOT EXISTS cadastral_verification_cases (
    id UUID PRIMARY KEY,
    comparison_run_id UUID NOT NULL REFERENCES comparison_runs(id) ON DELETE CASCADE,
    comparison_id UUID NULL REFERENCES parcel_comparisons(id) ON DELETE SET NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    officer_name VARCHAR(255),
    review_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS idx_cadastral_verification_run
ON cadastral_verification_cases(comparison_run_id);

CREATE INDEX IF NOT EXISTS idx_cadastral_verification_comparison
ON cadastral_verification_cases(comparison_id);
