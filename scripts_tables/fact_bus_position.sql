-- cristiangen16_coderhouse.fact_bus_position definition


CREATE TABLE IF NOT EXISTS cristiangen16_coderhouse.fact_bus_position
(
	idtrack INTEGER NOT NULL  ENCODE az64
	,dttmcatch TIMESTAMP WITHOUT TIME ZONE NOT NULL  ENCODE az64
	,idroute BIGINT   ENCODE az64
	,adlatitude DOUBLE PRECISION   ENCODE RAW
	,adlongitude DOUBLE PRECISION   ENCODE RAW
	,adspeed DOUBLE PRECISION   ENCODE RAW
	,adtimestamp BIGINT   ENCODE az64
	,addirection INTEGER   ENCODE az64
	,adagencyname VARCHAR(256)   ENCODE lzo
	,idagency INTEGER   ENCODE az64
	,adrouteshortname VARCHAR(256)   ENCODE lzo
	,idtransport VARCHAR(256)   ENCODE lzo
	,adtripheadsign VARCHAR(256)   ENCODE lzo
	,dttminsert TIMESTAMP WITHOUT TIME ZONE   ENCODE az64
	,PRIMARY KEY (idtrack, dttmcatch)
)
DISTSTYLE AUTO
 DISTKEY (idtrack)
;
ALTER TABLE cristiangen16_coderhouse.fact_bus_position owner to cristiangen16_coderhouse;