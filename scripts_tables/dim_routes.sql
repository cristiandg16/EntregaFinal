-- cristiangen16_coderhouse.dim_routes definition


CREATE TABLE IF NOT EXISTS cristiangen16_coderhouse.dim_routes
(
	route_id BIGINT NOT NULL  ENCODE az64
	,agency_id INTEGER   ENCODE az64
	,route_short_name VARCHAR(512)   ENCODE lzo
	,route_long_name VARCHAR(512)   ENCODE lzo
	,route_desc VARCHAR(512)   ENCODE lzo
	,route_type INTEGER   ENCODE az64
	,route_url VARCHAR(512)   ENCODE lzo
	,route_branding_url VARCHAR(512)   ENCODE lzo
	,route_color VARCHAR(512)   ENCODE lzo
	,route_text_color VARCHAR(512)   ENCODE lzo
	,PRIMARY KEY (route_id)
)
DISTSTYLE AUTO
;
ALTER TABLE cristiangen16_coderhouse.dim_routes owner to cristiangen16_coderhouse;