import psycopg2
import datetime

class postgres():
    # To improve the legibility of the queries, table names are not considered as an additional parameter.
    # Following table names are used: 
        # yellow: table stroing all the trips
        # zones: table storing the TLC zones
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
    

    def journeyTimeSeries(self, od, analysisInterval, timeInterval_Hour, timeInterval_Min, weekend):
        # This function would generate the time series of journey times for the given OD
        # at a given time interval e.g. timeInterval[0] = 9, timeInterval[1] = 10
        # for the analysis interval: datetime object (e.g. [datetime.date(2015,1,1), datetime.date(2015,1,31)])
        # If we are only interested in weekends, than weekend= True, otherwise False
        start_time = datetime.datetime.now()
        cur = self.conn.cursor()


        if(weekend):
            query = "SELECT id, (t_dropoff-t_pickup) \n" \
                    "FROM trips \n"\
                    "FULL JOIN zones z1 on st_contains(z1.geom, l_pickup) \n" \
                    "FULL JOIN zones z2 on st_contains(z2.geom, l_dropoff) \n" \
                    "WHERE t_pickup >= '{}' and t_pickup < '{}' \n" \
                    "AND (extract(hour from t_pickup) between {} and {}) \n" \
                    "AND (extract (minute from t_pickup) between {} and {}) \n" \
                    "AND z1.gid = {} and z2.gid = {} \n" \
                    "AND EXTRACT(DOW FROM t_pickup) in (0,6)".format(analysisInterval[0], analysisInterval[1], timeInterval_Hour[0], timeInterval_Hour[1], timeInterval_Min[0], timeInterval_Min[1], od[0], od[1])
        else:
            query = "SELECT id, (t_dropoff-t_pickup) \n" \
                    "FROM trips \n" \
                    "FULL JOIN zones z1 on st_contains(z1.geom, l_pickup) \n" \
                    "FULL JOIN zones z2 on st_contains(z2.geom, l_dropoff) \n" \
                    "WHERE t_pickup >= '{}' and t_pickup < '{}' \n" \
                    "AND (extract(hour from t_pickup) between {} and {}) \n" \
                    "AND (extract (minute from t_pickup) between {} and {}) \n" \
                    "AND z1.gid = {} and z2.gid = {} \n" \
                    "AND EXTRACT(DOW FROM t_pickup) in (1, 2, 3, 4, 5)".format(analysisInterval[0], analysisInterval[1],
                                                                     timeInterval_Hour[0], timeInterval_Hour[1],
                                                                     timeInterval_Min[0], timeInterval_Min[1], od[0],
                                                                     od[1])


        print(query)

        cur.execute(query)

        results = cur.fetchall()


        finish_time = datetime.datetime.now()
        timediff = (finish_time - start_time).total_seconds()
        cur.close()

        return timediff, results

def generate_journeyTimeSeries(connPostgres, od, analysisInterval, timeResolution, outFileName, weekend):
    # timeResolution is the temporal granularity of the analysis in MINUTES

    f_out = open(outFileName, 'w')


    P = postgres(*connPostgres)

    #numDays = (analysisInterval[1] - analysisInterval[0]).days
    #print(numDays)


    numTimeIntervals = 1440 / timeResolution #we want to see the numTimeIntervals to analyze in a DAY

    currentTime = analysisInterval[0]

    for i in range(int(numTimeIntervals)):
        tHr = currentTime.hour
        tMin = currentTime.minute
        #print(tHr, ": ", tMin)

        # Update the current time
        currentTime = currentTime + datetime.timedelta(minutes=timeResolution)

        timeInterval_Hour = [tHr, currentTime.hour]
        # If our temporal resolution is less than one hour, we have to account for it.
        if (timeResolution >= 60):
            timeInterval_Min = [0, 59]
            timeInterval_Hour[1] -= 1
        else:
            timeInterval_Min = [tMin, currentTime.minute]



        # However, we might need some adjustments:

        # If we are examining the last unit in an hour, there would be inconsistency:
        # E.g. [0 - 1] Hour, [45 - 0] Minute --> this should be --> [0 - 0] Hour, [45 - 59] Minute
        # If we are examining hourly basis, we must set the minutes to be between [0, 59] since the journey time minute could take any value
        if(timeInterval_Min[1] == 0):
            timeInterval_Hour[1] = timeInterval_Hour[0]
            timeInterval_Min[1] = 59


        # If we are examining the last temporal interval the following could arise: [23, -1] [45, 59]
        # That should be [23, 23] [45, 59]
        if(i == numTimeIntervals-1 and timeResolution >= 60):
            timeInterval_Hour[1] = timeInterval_Hour[0] + int(timeResolution/60) - 1

        print(timeInterval_Hour, timeInterval_Min) # timeInterval's are correctly generated!



        runTime, results = P.journeyTimeSeries(od, analysisInterval, timeInterval_Hour, timeInterval_Min, weekend)

        ids = []
        journeyTimes = []
        for r in results:
            # we can ignore the IDs of trips for simplicity
            #f_out.write(str(i) + ' ' + str(r[0]) + ' ' + format(r[1].total_seconds()/60, '.2f'))
            f_out.write(str(i) + ' ' + format(r[1].total_seconds() / 60, '.2f'))
            f_out.write('\n')

            # Copy paste to Excel:
            # =LEFT(A1, SEARCH(" ",A1, 1)) - to obtain the temporal unit ID
            # =RIGHT(A1,LEN(A1)-SEARCH(" ",A1,1)) - to obtain the journey time
            # make sure that they are numbers!



    f_out.close()




connPostgres = ["postgres", "postgres", "1234", "127.0.0.1", "5433"]
od = [132, 138] # define the OD pair
# 132: JFK
# 138: La Guardia
analysisInterval = [datetime.datetime(2015, 1, 1, 0, 0, 0), datetime.datetime(2015, 12, 31, 0, 0, 0)] #we can analyse the whole data set
timeResolution = 60 # temporal resolution in minutes.. ideally we can set it to be 60 minutes
weekend = False

if(weekend):
    outFile = str(od[0]) + '_' + str(od[1]) + '-' + str(timeResolution) + 'min' + '_weekend' + '.txt'
else:
    outFile = str(od[0]) + '_' + str(od[1]) + '-' + str(timeResolution) + 'min' + '_weekdays' + '.txt'

startTime = datetime.datetime.now()
generate_journeyTimeSeries(connPostgres, od, analysisInterval, timeResolution, outFile, weekend)
finish_time = datetime.datetime.now()
timediff = (finish_time - startTime).total_seconds()

print("Took: ", timediff, " seconds")
