CREATE SCHEMA IF NOT EXISTS raw_clinical;

CREATE TABLE IF NOT EXISTS raw_clinical.studies (
    nct_id VARCHAR(20) PRIMARY KEY,
    last_update_date TIMESTAMP WITH TIME ZONE,
    payload JSONB NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_studies_last_update 
ON raw_clinical.studies ((payload->'protocolSection'->'statusModule'->>'lastUpdatePostDate'));
