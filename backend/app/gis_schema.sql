CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS gis_layers (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    layer_type TEXT NOT NULL,
    geometry_type TEXT NOT NULL,
    crs INTEGER NOT NULL DEFAULT 4326,
    survey_id TEXT,
    visible BOOLEAN NOT NULL DEFAULT TRUE,
    opacity DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    style JSONB NOT NULL DEFAULT '{}'::jsonb,
    fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gis_features (
    id UUID PRIMARY KEY,
    layer_id UUID NOT NULL REFERENCES gis_layers(id) ON DELETE CASCADE,
    geom geometry(Geometry, 4326) NOT NULL,
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_crs INTEGER NOT NULL DEFAULT 4326,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS gis_features_geom_idx
ON gis_features
USING GIST (geom);

CREATE INDEX IF NOT EXISTS gis_features_layer_idx
ON gis_features(layer_id);

CREATE TABLE IF NOT EXISTS gis_rasters (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    public_url TEXT NOT NULL,
    survey_id TEXT,
    crs INTEGER,
    width INTEGER,
    height INTEGER,
    bands INTEGER,
    resolution_x DOUBLE PRECISION,
    resolution_y DOUBLE PRECISION,
    min_x DOUBLE PRECISION,
    min_y DOUBLE PRECISION,
    max_x DOUBLE PRECISION,
    max_y DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
