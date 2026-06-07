-- Healthcare Analytics - Fact Tables

CREATE TABLE IF NOT EXISTS fact.sales_fact (
    sales_id      BIGSERIAL PRIMARY KEY,
    sale_date     DATE NOT NULL,
    product_id    VARCHAR(20) NOT NULL REFERENCES dim.product_master(product_id),
    hcp_id        VARCHAR(20) NOT NULL REFERENCES dim.hcp_master(hcp_id),
    hospital_id   VARCHAR(20) NOT NULL REFERENCES dim.hospital_master(hospital_id),
    territory_id  VARCHAR(20) NOT NULL REFERENCES dim.territory_master(territory_id),
    rep_id        VARCHAR(20) NOT NULL REFERENCES dim.sales_rep_master(rep_id),
    units_sold    INTEGER NOT NULL DEFAULT 0,
    gross_sales   NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_sales     NUMERIC(15,2) NOT NULL DEFAULT 0,
    discount_pct  NUMERIC(5,2) NOT NULL DEFAULT 0,
    channel       VARCHAR(50) NOT NULL DEFAULT 'Direct'
);

CREATE TABLE IF NOT EXISTS fact.prescription_fact (
    rx_id           BIGSERIAL PRIMARY KEY,
    rx_date         DATE NOT NULL,
    product_id      VARCHAR(20) NOT NULL REFERENCES dim.product_master(product_id),
    hcp_id          VARCHAR(20) NOT NULL REFERENCES dim.hcp_master(hcp_id),
    patient_count   INTEGER NOT NULL DEFAULT 0,
    rx_count        INTEGER NOT NULL DEFAULT 0,
    new_rx_count    INTEGER NOT NULL DEFAULT 0,
    refill_rx_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fact.interaction_fact (
    interaction_id      BIGSERIAL PRIMARY KEY,
    interaction_date    TIMESTAMPTZ NOT NULL,
    rep_id              VARCHAR(20) NOT NULL REFERENCES dim.sales_rep_master(rep_id),
    hcp_id              VARCHAR(20) NOT NULL REFERENCES dim.hcp_master(hcp_id),
    interaction_type    VARCHAR(50) NOT NULL,
    duration_minutes    INTEGER NOT NULL DEFAULT 0,
    outcome             VARCHAR(100),
    samples_provided    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS audit.query_log (
    log_id        BIGSERIAL PRIMARY KEY,
    session_id    VARCHAR(100),
    user_id       VARCHAR(100),
    question      TEXT,
    intent        VARCHAR(50),
    sql_executed  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
