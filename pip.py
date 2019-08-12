#----------------------------------------------------------------------
# This script finds the polygon which a query point is in
#----------------------------------------------------------------------
import psycopg2
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from haversine import haversine, Unit

# Inputs:
randomID = 556677
# DB Connection settings:
connPostgres = ["postgres", "postgres", "1234", "127.0.0.1", "5433"]
connMongoDB = ["localhost", 27017, "nyc"]


# This function returns the lat/lon of the pickup location of an input trip
# MongoDB is used to determine the coordinates
def findCoordinates(M_conn, tripID):
    document = M_conn.nyc2015.find_one({"properties.ID_Postgres": tripID})
    #print(document)
    x = document['geometry_pk']['coordinates'][0]
    y = document['geometry_pk']['coordinates'][1]
    return x, y

class mongoDB():
    def __init__(self,host, port, dbName):
        client = MongoClient(host, port)
        self.db = client[dbName]

        try:
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
            print("Connected to MongoDB Server\n\n")
            print("Avaiable collections within the database:", self.db.list_collection_names() )
            # Switch to nyc2015 collection
            self.nyc2015 = self.db.nyc2015
        except ConnectionFailure:
            print("Mongodb Server not available\n\n")

    def pip(self,tripID):
        #This query retries the polygon in which the pickup of tripID resides
        #This query takes coordinates. And finding the polygons name which the point in inside.


        document = self.nyc2015.find_one({"properties.ID_Postgres": tripID})
        xP = document['geometry_pk']['coordinates'][0]
        yP = document['geometry_pk']['coordinates'][1]


        # Find the Origin Zone
        queryPickup = {}
        queryPickup["geometry"] = {
            u"$geoIntersects": {
                u"$geometry": {
                    u"type": u"Point",
                    u"coordinates": [
                        xP, yP
                    ]
                }
            }
        }


        # Record the execution time of the query
        start_time = datetime.datetime.now()

        cursorPickup = self.nyc2015.find(queryPickup)

        # It is possible for a point to be OUTSIDE of all zones
        # To handle that, we need to use a flag!
        flag = 0

        for doc in cursorPickup:
            # print(x, ",", y, " -------------------> ", doc['properties']['zone'])
            # Zone name: doc['properties']['zone']
            flag = 1
            polygonID = doc['properties']['LocationID']
        if (flag == 0):
            polygonID = None


        finish_time = datetime.datetime.now()
        timediff = (finish_time - start_time).total_seconds()

        del cursorPickup

        return timediff, polygonID


class postgres():
    def __init__(self, dbName, userName, pswd, host, port):
        try:
            self.conn = psycopg2.connect(database=dbName,
                            user=userName,
                            password=pswd,
                            host=host,
                            port=port)
            print("Connected to PostgreSQL Server")
        except:
            print("Postgres connection failed!")


    def pip(self, tripID):
        # pip: point_in_polygon
        # This method returns the Origin - Destination polygon of the pickup location of the trip ID
        cur = self.conn.cursor()

        q_pip = "SELECT z1.gid as Origin \n" \
                "FROM trips t \n" \
                "FULL JOIN zones z1 ON ST_Contains(z1.geom, t.l_pickup) \n" \
                "WHERE t.id = {}".format(tripID)

        start_time = datetime.datetime.now()
        cur.execute(q_pip)
        finish_time = datetime.datetime.now()

        # Keep the OD of the trip
        polygonID = cur.fetchall()[0][0]

        cur.close

        return (finish_time - start_time).total_seconds(), polygonID



# Create the database connection objects
M = mongoDB(*connMongoDB)
P = postgres(*connPostgres)

t_M, polygonID_M = M.pip(randomID)

print("MongoDB")
print("\tExecution Time: ", t_M)
print("\tPolygon ID: ", polygonID_M)

t_P, polygonID_P = P.pip(randomID)

print("Postgres")
print("\tExecution Time:  ", t_P)
print("\tPolygon ID: ", polygonID_P)




