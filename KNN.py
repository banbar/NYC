#----------------------------------------------------------------------
# This script finds the KNN of a random point in Postgres and MongoDB.
#----------------------------------------------------------------------
import psycopg2
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from haversine import haversine, Unit

# Inputs:
kValue = 30
randomID = 55116350
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

    def k_NN(self, tripID, k):
        # Retrieve the document
        document = self.nyc2015.find_one({"properties.ID_Postgres": tripID})
        # Find the coordinates of the trip
        x = document['geometry_pk']['coordinates'][0]
        y = document['geometry_pk']['coordinates'][1]
        # print(x,y) - OK

        # Construct the MongoDB query
        query = {}
        query["geometry_pk"] = {
            u"$nearSphere": {
                u"$geometry": {
                    u"type": u"Point",
                    u"coordinates": [
                        x, y
                    ]
                }
            }
        }

        # Record the execution time of the query
        start_time = datetime.datetime.now()
        cursor = self.nyc2015.find(query).limit(k)
        finish_time = datetime.datetime.now()
        timediff = (finish_time - start_time).total_seconds()

        k_NN = set()
        for doc in cursor:
            k_NN.add(doc['properties']['ID_Postgres'])

        del cursor
        return timediff, k_NN


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


    def k_NN_v2(self, tripID,k):
        # This query determines the k_NN of a pickup location of a trip using id insertion
        # It has a similar idea to MongoDB query

        cur = self.conn.cursor()
        query = "SELECT id " \
            "FROM trips " \
            "ORDER BY l_pickup <-> (select l_pickup from trips where id = {})" \
            "limit {}".format(tripID, k)

        # We want to record the time of execution of the query
        start_time = datetime.datetime.now()
        cur.execute(query)
        finish_time = datetime.datetime.now()
        timediff = (finish_time - start_time).total_seconds()

        # It is also important to have the NNs for comparison with other queries
        rows = cur.fetchall()
        k_NN = set()
        for row in rows:
            k_NN.add(row[0])

        cur.close()
        return timediff, k_NN



connPostgres = ["postgres", "postgres", "1234", "127.0.0.1", "5433"]
connMongoDB = ["localhost", 27017, "nyc"]

# Create the database connection objects
M = mongoDB(*connMongoDB)
P = postgres(*connPostgres)




# We also want to analyse the Haversine distance between detected neighbours and the query point
# Spatial accuracy assessment
# Initialize the maximum Haversine distances
maxH_P = 0 # Max Haversine distance in Postgres
maxH_M = 0 # Max Haversine distance in MongoDB

# Initialize the neighbors for Haversine analysis
maxH_P_neighID = -1
maxH_M_neighID = -1


# The coordinates of the pickup location
tripX, tripY = findCoordinates(M, randomID)
trip = (tripY, tripX)

# Run k-NN for Postgres-v2
t_Postgres, set_Postgres = P.k_NN_v2(randomID, kValue)

# Run k-NN for MongoDB
t_MongoDB, set_MongoDB = M.k_NN(randomID, kValue)

# Determine the match percentage
intersection = set_Postgres.intersection(set_MongoDB)


# Haversine Distance analysis
set_Postgres = list(set_Postgres)
# Find the max Haversine distance between the pickup location of the trip and its neighbours
for i in range(len(set_Postgres)):
    # The coordinates of the next neasrest neighbour
    #print(set_Postgres[i])

    neighX, neighY = findCoordinates(M, set_Postgres[i])
    neigh = (neighY, neighX)
    # Calculate the Haversine distance:
    d = haversine(trip, neigh, unit=Unit.METERS) # (lat-lon) - (lat-lon)
    if(d > maxH_P):
        maxH_P = d
        maxH_P_tripID = randomID
        maxH_P_neighID = set_Postgres[i]

set_MongoDB = list(set_MongoDB)
# Find the max Haversine distance between the pickup location of the trip and its neighbours
for i in range(len(set_MongoDB)):
    # The coordinates of the next neasrest neighbour
    neighX, neighY = findCoordinates(M, set_MongoDB[i])
    neigh = (neighY, neighX)
    # Calculate the Haversine distance:
    d = haversine(trip, neigh, unit=Unit.METERS)  # (lat-lon) - (lat-lon)
    if (d > maxH_M):
        maxH_M = d
        maxH_M_tripID = randomID
        maxH_M_neighID = set_Postgres[i]

print("Max Haversine - Postgres: ", maxH_P)
print("Max Haversine - MongoDB: ", maxH_M)

