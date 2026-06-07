-- Healthcare Analytics - Indexes

CREATE INDEX IF NOT EXISTS idx_sales_fact_date_territory_product
    ON fact.sales_fact (sale_date, territory_id, product_id);

CREATE INDEX IF NOT EXISTS idx_sales_fact_hcp_date
    ON fact.sales_fact (hcp_id, sale_date);

CREATE INDEX IF NOT EXISTS idx_prescription_fact_date_product
    ON fact.prescription_fact (rx_date, product_id);

CREATE INDEX IF NOT EXISTS idx_prescription_fact_hcp
    ON fact.prescription_fact (hcp_id, rx_date);

CREATE INDEX IF NOT EXISTS idx_interaction_fact_hcp
    ON fact.interaction_fact (hcp_id, interaction_date);

CREATE INDEX IF NOT EXISTS idx_hcp_specialty_city_tier
    ON dim.hcp_master (specialty, city, tier);

CREATE INDEX IF NOT EXISTS idx_hcp_territory
    ON dim.hcp_master (territory_id);

CREATE INDEX IF NOT EXISTS idx_hospital_territory
    ON dim.hospital_master (territory_id);

CREATE INDEX IF NOT EXISTS idx_product_therapeutic_area
    ON dim.product_master (therapeutic_area);

CREATE INDEX IF NOT EXISTS idx_sales_fact_sale_date_brin
    ON fact.sales_fact USING BRIN (sale_date);

CREATE INDEX IF NOT EXISTS idx_prescription_fact_rx_date_brin
    ON fact.prescription_fact USING BRIN (rx_date);
