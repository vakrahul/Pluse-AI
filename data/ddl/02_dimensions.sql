-- Healthcare Analytics - Dimension Tables

CREATE TABLE IF NOT EXISTS dim.territory_master (
    territory_id    VARCHAR(20) PRIMARY KEY,
    territory_name  VARCHAR(200) NOT NULL,
    region          VARCHAR(100) NOT NULL,
    zone            VARCHAR(100) NOT NULL,
    country         VARCHAR(50) NOT NULL DEFAULT 'India',
    sales_target    NUMERIC(15,2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dim.hospital_master (
    hospital_id     VARCHAR(20) PRIMARY KEY,
    hospital_name   VARCHAR(300) NOT NULL,
    hospital_type   VARCHAR(50) NOT NULL,
    bed_count       INTEGER NOT NULL DEFAULT 0,
    city            VARCHAR(100) NOT NULL,
    state           VARCHAR(50) NOT NULL,
    territory_id    VARCHAR(20) NOT NULL REFERENCES dim.territory_master(territory_id),
    latitude        NUMERIC(10,7),
    longitude       NUMERIC(10,7)
);

CREATE TABLE IF NOT EXISTS dim.product_master (
    product_id        VARCHAR(20) PRIMARY KEY,
    product_name      VARCHAR(200) NOT NULL,
    brand_name        VARCHAR(200) NOT NULL,
    therapeutic_area  VARCHAR(100) NOT NULL,
    indication        VARCHAR(200) NOT NULL,
    molecule          VARCHAR(100) NOT NULL,
    launch_date       DATE NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    unit_price        NUMERIC(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dim.sales_rep_master (
    rep_id        VARCHAR(20) PRIMARY KEY,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(200) NOT NULL UNIQUE,
    territory_id  VARCHAR(20) NOT NULL REFERENCES dim.territory_master(territory_id),
    manager_id    VARCHAR(20) REFERENCES dim.sales_rep_master(rep_id),
    hire_date     DATE NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dim.hcp_master (
    hcp_id              VARCHAR(20) PRIMARY KEY,
    npi_number          VARCHAR(15) NOT NULL UNIQUE,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    specialty           VARCHAR(100) NOT NULL,
    sub_specialty       VARCHAR(100),
    tier                VARCHAR(20) NOT NULL CHECK (tier IN ('Gold', 'Silver', 'Bronze')),
    segmentation_score  NUMERIC(5,2) NOT NULL CHECK (segmentation_score BETWEEN 0 AND 100),
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(50) NOT NULL,
    country             VARCHAR(50) NOT NULL DEFAULT 'India',
    hospital_id         VARCHAR(20) NOT NULL REFERENCES dim.hospital_master(hospital_id),
    territory_id        VARCHAR(20) NOT NULL REFERENCES dim.territory_master(territory_id),
    is_kol              BOOLEAN NOT NULL DEFAULT FALSE,
    referral_count      INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE VIEW meta.agent_schema AS
SELECT table_schema, table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema IN ('dim', 'fact')
ORDER BY table_schema, table_name, ordinal_position;
