def main():
    import mysql.connector

    values = readFile("sun_update.csv")
    importToDB(mysql, values)

def readFile(inputfile):
    file = open(inputfile, "r")
    file.readline();
    dbvalues = []
    for line in file:
        strippedLine = line.strip()
        splitLine = strippedLine.split(",")
        lineValues = splitLine[2], splitLine[3], splitLine[8], splitLine[4], splitLine[6]
        dbvalues.append(lineValues)
    file.close()
    return dbvalues

def importToDB(mysql, values):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="solar_expres"
    )

    mycursor = mydb.cursor()

    createTable(mycursor)

    sql = "INSERT INTO radialvelocity (mjd, radVelocity, expTime, ev, filename) VALUES (%s, %s, %s, %s, %s)"

    mycursor.executemany(sql, values)

    mydb.commit()

    print(mycursor.rowcount, "records inserted")

def createTable(mycursor):
    drop = "DROP TABLE IF EXISTS `radialvelocity`;"

    create = "CREATE TABLE `radialvelocity` (`id` int(11) NOT NULL AUTO_INCREMENT,`mjd` decimal(9, 4) DEFAULT NULL,`radVelocity` decimal(7, 4) DEFAULT NULL, `expTime` decimal(7, 3) DEFAULT NULL,`ev` decimal(6, 3) DEFAULT NULL, `filename` varchar(45) DEFAULT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"

    mycursor.execute(drop);
    mycursor.execute(create);

main()
