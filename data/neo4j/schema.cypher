// Healthcare Analytics Graph Schema

CREATE CONSTRAINT hcp_id IF NOT EXISTS FOR (h:HCP) REQUIRE h.hcp_id IS UNIQUE;
CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE;
CREATE CONSTRAINT hospital_id IF NOT EXISTS FOR (h:Hospital) REQUIRE h.hospital_id IS UNIQUE;
CREATE CONSTRAINT territory_id IF NOT EXISTS FOR (t:Territory) REQUIRE t.territory_id IS UNIQUE;
CREATE CONSTRAINT rep_id IF NOT EXISTS FOR (r:SalesRep) REQUIRE r.rep_id IS UNIQUE;

CREATE INDEX hcp_specialty IF NOT EXISTS FOR (h:HCP) ON (h.specialty);
CREATE INDEX hcp_city IF NOT EXISTS FOR (h:HCP) ON (h.city);
CREATE INDEX hcp_tier IF NOT EXISTS FOR (h:HCP) ON (h.tier);
