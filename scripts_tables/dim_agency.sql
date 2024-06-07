-- cristiangen16_coderhouse.dim_agency definition


CREATE TABLE IF NOT EXISTS cristiangen16_coderhouse.dim_agency
(
	agency_id INTEGER NOT NULL  ENCODE az64
	,agency_name VARCHAR(512)   ENCODE lzo
	,agency_url VARCHAR(512)   ENCODE lzo
	,agency_timezone VARCHAR(512)   ENCODE lzo
	,agency_lang VARCHAR(512)   ENCODE lzo
	,agency_phone VARCHAR(512)   ENCODE lzo
	,agency_branding_url VARCHAR(512)   ENCODE lzo
	,agency_fare_url VARCHAR(512)   ENCODE lzo
	,agency_email VARCHAR(512)   ENCODE lzo
	,PRIMARY KEY (agency_id)
)
DISTSTYLE AUTO
;
ALTER TABLE cristiangen16_coderhouse.dim_agency owner to cristiangen16_coderhouse;