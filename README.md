# New York City - Query Performance Analyses of Postgres and MongoDB
This repository contains the code and experiments to analyse openly available taxi dataset of New York City.The content is optimised for [yellow taxi trips of 2015](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

>:white_check_mark: **If you are using this plugin for scientific research, please cite the paper** <a href=https://link.springer.com/chapter/10.1007/978-3-030-58232-6_3>`<b>Spatial Query Performance Analyses on a Big Taxi Trip Origin–Destination Dataset</b></a> 


## Contents:
* nyc_trips_table_create.sql
  * Creating the tables in Postgres by assigning a unique ID to each trip. 
  * It is important to assign an appropriate data type to each attribute.
  * Lab task: Investigate the difference between the size of the created tables.  
* postgres2GeoJSON.py
  * Creating the GeoJSON files that could be imported into MongoDB.
* KNN.py
  * Detecting the KNN of a query point
* pip.py
  * Point-in-Polygon query (pip). Given a query point, it determines the polygon which it resides in. 
* Journey Time Analysis
  * This folder includes the code and data to visualise the journey times from John F. Kennedy airport to LaGuardia.
  
