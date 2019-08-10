# New York City - Query Performance Analyses of Postgres and MongoDB
This repository contains the code and experiments to analyse openly available taxi dataset of New York City.The content is optimised for .  [yellow taxi trips of 2015](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

## Contents:
* nyc_yellow_table_create.sql
  * Creating the tables in Postgres by assigning a unique ID to each trip. 
  * It is important to assign an appropriate data type to each attribute.
  * Lab task: Investigate the difference between the size of the created tables.  
* postgres2GeoJSON.py
 * Creating the GeoJSON files that could be imported into MongoDB.
  
