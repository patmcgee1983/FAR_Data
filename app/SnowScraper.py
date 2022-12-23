# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 22:09:54 2020

@author: Pat McGee

This script scrapes the Fernie Alpine Resort Webpage for the current lift/bowl status, weather and snow conditions
Every time it sees a change within operating hours it stores the information in the far_data database

"""
import os


def scrape():
    import requests
    from bs4 import BeautifulSoup
    import re
    import pymysql
    from datetime import datetime

    print("Starting Scraper at ", datetime.now())

    try:
        cnx = pymysql.connect(user=os.getenv("db_user"),
                              password=os.getenv("db_password"),
                              host=os.getenv("db_host"),
                              database=os.getenv("db_db"))
    except:
        print("Can't connect to SQL Server...")
        return False

    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    page = requests.get('https://skifernie.com/refresh/refresh.php')

    soup = BeautifulSoup(page.text, 'html.parser')

    # if (parent.document.getElementById('headerLast24')) {parent.document.getElementById('headerLast24').innerHTML= '0';}

    pageString = str(soup)

    objects = []
    values = []
    runObjects = []
    runValues = []

    # print(pageString)
    r1 = re.findall(r"^.*parent.document.getElementById.*$", pageString, re.MULTILINE)

    # print(len(r1))
    i = 0;

    print("Scraping Fernie Snow Report...")

    for word in r1:
        objects.append("")
        values.append("")

        # print(word)
        # print("\n\n")

        quoted = re.compile("getElementById\('[^']*'")

        for value in quoted.findall(word):
            objects[i] = value.replace("getElementById('", "").replace("'", "")

        quoted = re.compile('"[^"]*"')

        for value in quoted.findall(word):
            if objects[i] == 'SnowreportComments':
                values[i] = r1[i].replace("if (parent.document.getElementById('SnowreportComments')) {parent.document.getElementById('SnowreportComments').innerHTML= \"", '').replace("\";}","")
            else:
                values[i] = cleanhtml(value.replace('"', ''))

        i = i + 1

    ###############################################################################
    #                       Bowl Status Scraper
    ###############################################################################
    bowlsObjects = ["snowReportCedarBowl", "snowReportLizardBowl", "snowReportCurrieBowl", "snowReportTimberBowl",
                    "snowReportSiberiaBowl"]

    # --------------- Iterate through the bowls and get their status's ---------------
    i = 0
    for bowls in bowlsObjects:
        tempRunObjects = []
        currentIndex = objects.index(bowlsObjects[i])
        bowlString = values[currentIndex]
        bowlString = re.sub('Open', ",Open", bowlString)
        bowlString = re.sub('Closed', ",Closed", bowlString)
        bowlString = re.sub('Stand By', ",Stand By", bowlString)

        tempRunObjects = bowlString.split(",")
        tempRunObjects.pop(0)

        for bowl in tempRunObjects:
            tempString = re.sub('Open', "Open,", bowl)
            tempString = re.sub('Closed', "Closed,", tempString)
            tempString = re.sub('Stand By', "Stand By,", tempString)

            tempArray = tempString.split(",")
            runObjects.append(tempArray[1])
            runValues.append(tempArray[0])

        i = i + 1
        objects.pop(currentIndex)
        values.pop(currentIndex)

    bowlUpdateIndex = objects.index("snowReportTH_SnowreportBowlsSaveDate")
    bowlsLastUpdate = values[bowlUpdateIndex]

    i = 0
    for x in runObjects:
        # print(runObjects[i] + ": " + runValues[i])
        i = i + 1

    # for x in range(0, len(values)):
    #    print(objects[x])
    #    print(values[x])

    mycursor = cnx.cursor()

    mycursor.execute("SHOW TABLES LIKE '%bowls%'; ")
    myresult = mycursor.fetchall()

    if (not myresult):
        print("no bowl table found.... creating")
        mycursor.execute(
            "CREATE TABLE `far_data`.`bowls` (`Id` INT UNSIGNED NOT NULL AUTO_INCREMENT,PRIMARY KEY (`Id`));")

    i = 0

    in_time = datetime.strptime(bowlsLastUpdate.strip(), "%B %d, %Y | %I:%M%p")
    bowlsLastUpdate = datetime.strftime(in_time, "%Y-%m-%d %H:%M:%S")

    sql = "SHOW COLUMNS FROM `bowls` LIKE 'LastUpdate';"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if (not myresult):
        sql = "ALTER TABLE `far_data`.`bowls` ADD COLUMN LastUpdate DATETIME UNIQUE;"
        mycursor.execute(sql)

    sql = "SELECT * FROM bowls WHERE LastUpdate = '" + bowlsLastUpdate + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if (not myresult):
        print("Bowl status were detected at " + str(datetime.now()) + "!")
        sql = "INSERT INTO bowls (LastUpdate) VALUES ('" + bowlsLastUpdate + "')"
        mycursor.execute(sql)

        for bowl in runObjects:

            runObjects[i] = runObjects[i].replace(" ", "_")
            runObjects[i] = re.sub(r'\W+', '', runObjects[i])

            sql = "SHOW COLUMNS FROM `bowls` LIKE '" + runObjects[i] + "';"
            myresult = mycursor.execute(sql)
            myresult = mycursor.fetchall()

            if (not myresult):
                print("Column " + runObjects[i] + " not found, creating...")
                sql = "ALTER TABLE `far_data`.`bowls` ADD COLUMN `" + runObjects[i] + "` VARCHAR(45);"
                mycursor.execute(sql)
            print("Writing value to column " + runObjects[i])
            sql = "UPDATE bowls SET " + runObjects[i] + "='" + runValues[i].replace("'",
                                                                                    "`") + "' WHERE LastUpdate = '" + bowlsLastUpdate + "'"
            mycursor.execute(sql)

            i = i + 1
            cnx.commit()
    else:
        print("No bowl updates")

    ###############################################################################
    #                       New Snow Status Scraper
    ###############################################################################

    newSnowUpdateIndex = objects.index("snowReportTH_SnowreportRecentSnowSaveDate")
    newSnowLastUpdate = values[newSnowUpdateIndex]
    in_time = datetime.strptime(newSnowLastUpdate.strip(), "%B %d, %Y | %I:%M%p")
    newSnowLastUpdate = datetime.strftime(in_time, "%Y-%m-%d %H:%M:%S")

    newSnowObjects = []
    newSnowValues = []

    mycursor.execute("SHOW TABLES LIKE '%NewSnow%'; ")
    myresult = mycursor.fetchall()

    if (not myresult):
        print("No newSnow table found.... creating")
        mycursor.execute(
            "CREATE TABLE `far_data`.`NewSnow` (`Id` INT UNSIGNED NOT NULL AUTO_INCREMENT,PRIMARY KEY (`Id`));")

    sql = "SHOW COLUMNS FROM `NewSnow` LIKE 'LastUpdate';"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if (not myresult):
        sql = "ALTER TABLE `far_data`.`NewSnow` ADD COLUMN LastUpdate DATETIME UNIQUE;"
        mycursor.execute(sql)

    sql = "SELECT * FROM `far_data`.`NewSnow` WHERE LastUpdate = '" + newSnowLastUpdate + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if (not myresult):

        print("New Snow updates were detected at " + str(datetime.now()) + "!")
        sql = "INSERT INTO NewSnow (LastUpdate) VALUES ('" + newSnowLastUpdate + "')"
        mycursor.execute(sql)

        for idx, val in enumerate(objects):
            # print(val)
            if "snowReportNewSnowFall" in val:
                newSnowObjects.append(val)
                newSnowValues.append(values[idx].replace(" ", ""))

        for idx, val in enumerate(newSnowObjects):
            currentSnowObject = val
            currentNewSnowValue = newSnowValues[idx].replace(" ", "")

            i = 0

            sql = "SHOW COLUMNS FROM `NewSnow` LIKE '" + currentSnowObject + "';"
            myresult = mycursor.execute(sql)
            myresult = mycursor.fetchall()

            if (not myresult):
                print("Column " + currentSnowObject + " not found, creating...")
                sql = "ALTER TABLE `far_data`.`NewSnow` ADD COLUMN `" + currentSnowObject + "` VARCHAR(45);"
                mycursor.execute(sql)
            print("Writing value to column " + currentSnowObject)
            sql = "UPDATE NewSnow SET " + currentSnowObject + "='" + currentNewSnowValue + "' WHERE LastUpdate = '" + newSnowLastUpdate + "'"
            mycursor.execute(sql)

            cnx.commit()

    else:
        print("No new snow updates")

    ###############################################################################
    #                       Temperature Updates
    ###############################################################################

    temperatureUpdateIndex = objects.index("snowReportTH_SnowreportBowlsSaveDate")
    tempLastUpdate = values[temperatureUpdateIndex]
    in_time = datetime.strptime(tempLastUpdate.strip(), "%B %d, %Y | %I:%M%p")
    tempLastUpdate = datetime.strftime(in_time, "%Y-%m-%d %H:%M:%S")

    temperatureObjects = []
    temperatureValues = []

    mycursor.execute("SHOW TABLES LIKE '%Temperatures%'; ")
    myresult = mycursor.fetchall()

    if (not myresult):
        print("No Temperatures table found.... creating")
        mycursor.execute(
            "CREATE TABLE `far_data`.`Temperatures` (`Id` INT UNSIGNED NOT NULL AUTO_INCREMENT,PRIMARY KEY (`Id`));")

    sql = "SHOW COLUMNS FROM `Temperatures` LIKE 'LastUpdate';"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if (not myresult):
        sql = "ALTER TABLE `far_data`.`Temperatures` ADD COLUMN LastUpdate DATETIME UNIQUE;"
        mycursor.execute(sql)

    sql = "SELECT * FROM `far_data`.`Temperatures` WHERE LastUpdate = '" + tempLastUpdate + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if (not myresult):

        print("New Temperature updates were detected at " + str(datetime.now()) + "!")
        sql = "INSERT INTO Temperatures (LastUpdate) VALUES ('" + tempLastUpdate + "')"
        mycursor.execute(sql)

        for idx, val in enumerate(objects):
            # print(val)
            if "snowReportWeather" in val:
                temperatureObjects.append(val)
                temperatureValues.append(values[idx].replace(" ", ""))
                print("Added ")

        for idx, val in enumerate(temperatureObjects):
            currentTempObject = val
            currentTempValue = temperatureValues[idx].replace(" ", "")

            i = 0

            sql = "SHOW COLUMNS FROM `Temperatures` LIKE '" + currentTempObject + "';"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()

            if (not myresult):
                print("Column " + currentTempObject + " not found, creating...")
                sql = "ALTER TABLE `far_data`.`Temperatures` ADD COLUMN `" + currentTempObject + "` VARCHAR(45);"
                mycursor.execute(sql)
            print("Writing value to column " + currentTempObject)
            sql = "UPDATE Temperatures SET " + currentTempObject + "='" + currentTempValue + "' WHERE LastUpdate = '" + tempLastUpdate + "'"
            mycursor.execute(sql)
            cnx.commit()
    else:
        print("No temperature updates")

    ###############################################################################
    #                       Comments Update
    ###############################################################################

    commentsLastUpdateIndex = objects.index("snowReportTH_SnowreportCommentsSaveDate")
    commentsLastUpdate = values[commentsLastUpdateIndex]

    in_time = datetime.strptime(commentsLastUpdate.strip(), "%B %d, %Y | %I:%M%p")
    commentsLastUpdate = datetime.strftime(in_time, "%Y-%m-%d %H:%M:%S")

    mycursor.execute("SHOW TABLES LIKE '%Comments%'; ")
    myresult = mycursor.fetchall()

    if (not myresult):
        print("No Comments table found.... creating")
        mycursor.execute(
            "CREATE TABLE `far_data`.`Comments` (`Id` INT UNSIGNED NOT NULL AUTO_INCREMENT,PRIMARY KEY (`Id`));")

    sql = "SHOW COLUMNS FROM `Comments` LIKE 'LastUpdate';"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if (not myresult):
        sql = "ALTER TABLE `far_data`.`Comments` ADD COLUMN LastUpdate DATETIME UNIQUE;"
        mycursor.execute(sql)

    sql = "SHOW COLUMNS FROM `Comments` LIKE 'Comments';"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if (not myresult):
        sql = "ALTER TABLE `far_data`.`Comments` ADD COLUMN Comments VARCHAR(2000);"
        mycursor.execute(sql)

    sql = "SELECT * FROM `far_data`.`Comments` WHERE LastUpdate = '" + commentsLastUpdate + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if (not myresult):
        print("New Comments updates were detected at " + str(datetime.now()) + "!")
        sql = "INSERT INTO Comments (LastUpdate, Comments) VALUES ('{0}', '{1}')".format(commentsLastUpdate, values[objects.index("SnowreportComments")].replace('"', "").replace("\\n", "").replace("\\r", ""))
        mycursor.execute(sql)

    else:
        print("No new comments")

    cnx.commit()
    print("done")
    mycursor.close()
    cnx.close()


print("Scraping")

try:
    scrape()

except Exception as e:
    print("Encountered error while scraping")
    print(e)

