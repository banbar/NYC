# New York City - Query Performance Analyses of Postgres and MongoDB
This repository contains the code and experiments to analyse openly available taxi dataset of New York City.The content is optimised for .  [yellow taxi trips of 2015](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

## Contents:
* nyc_yellow_table_create
  * This file is used to create the tables in Postgres by assigning a unique ID to each trip. 
  * Lab task: Investigate the difference between the size of the tables. 
    

## PostGIS - SQL
1. Import the polygon shapefile into PostGIS
2. Create the *centroids* table
   1. gid (geometry_id) - serial
   2. name - varchar(40)
   3. geom (geometry) - geometry(point,*SRID*)
3. Populate the centroids table (st_centroid)
4. Create the *edges* table
    1. gid (geometry_id) - serial
    2. origin - text
    3. destination - text
    4. cost (weight) - float
    5. geom (geometry) - geometry(LineString, *SRID*)
    6. origin_gid - integer
    7. destination_gid - integer
5. Populate the edges table (st_intersects) 

- - - -
The MST of Turkish cities and districts are found by using the Kruskal's algorithm which is implemented in Python (previously shared on [Twitter](https://twitter.com/B_Anbar/status/1087787095748423687)):

*The aim of this project is to integrate all the process into a QGIS plugin such that whenever the user inputs a shp file, the MST is provided back.*

![MST of Turkish Cities](https://pbs.twimg.com/media/DxiXP_WX0AEZrHp.jpg)


![MST of districts](https://pbs.twimg.com/media/Dz--HO9X0AEYTZn.jpg:large)
