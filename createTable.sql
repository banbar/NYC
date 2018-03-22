--From staging to production

-- We need to have the postgis extension enabled.
create extension postgis

--1. Create the table
CREATE TABLE yellow (
  id serial primary key,
  vendorid character varying(1),
  t_pickup timestamp without time zone,
  t_dropoff timestamp without time zone,
  num_passengers smallint,
  trip_distance real,
  l_pickup_lon double precision,
  l_pickup_lat double precision,
  ratecodeid character(2),
  flag_store character(1),
  l_dropoff_lon double precision,
  l_dropoff_lat double precision,
  payment_type character(1),
  fare_amount real,
  extra real,
  mta_tax real,
  surcharge real,
  tip real,
  tolls real,
  total real,
  l_pickup geometry(point,4326),
  l_dropoff geometry(point,4326)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.yellow_taxis_staging
  OWNER TO postgres;



-- 2. Insert the records and create the points:
INSERT INTO yellow (vendorid, t_pickup, t_dropoff, num_passengers, trip_distance, l_pickup_lon, l_pickup_lat, ratecodeid, flag_store, l_dropoff_lon, l_dropoff_lat, payment_type, fare_amount, extra, mta_tax, surcharge, tip, tolls, total, l_pickup, l_dropoff)
SELECT vendorid, t_pickup, t_dropoff, num_passengers, trip_distance, l_pickup_lon, l_pickup_lat, ratecodeid, flag_store, l_dropoff_lon, l_dropoff_lat, payment_type, fare_amount, extra, mta_tax, surcharge, tip, tolls, total,
ST_SetSRID(ST_Point(l_pickup_lon, l_pickup_lat),4326) As l_pickup,
ST_SetSRID(ST_Point(l_dropoff_lon,l_dropoff_lat),4326) As l_dropoff
FROM yellow_taxis_staging;

-- Note: Another SRID like (2163) might be more suitable, but for now we rely on WGS84.
-- ST_Transform(ST_SetSRID(ST_Point(l_pickup_lon,l_pickup_lat),4326),2163) As l_pickup,



select *
from yellow
limit 1

