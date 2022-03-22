import psycopg2
import pyodbc
import sys
import pymysql
import pandas as pd
from main.CONFIG_READER.read import get_details


# server = get_details("SQL_SERVER", "server")
# database = get_details("SQL_SERVER", "database")
# username = get_details("SQL_SERVER", "username")
# password = get_details("SQL_SERVER", "password")
# driver = get_details("SQL_SERVER", "driver")

#server = "summermiemieserver.database.windows.net"
#database = "summermiemiesqldb"
#username = "miemie_login"
#password = "e_Paswrd?!"
#driver = "{ODBC Driver 17 for SQL Server}"

postgre_database = get_details("POSTGRESQL", "database")
postgre_user = get_details("POSTGRESQL", "username")
postgre_host = get_details("POSTGRESQL", "host")
postgre_password = get_details("POSTGRESQL", "password")
postgre_port = get_details("POSTGRESQL", "port")




def getMySQL():
    """
        Returns connection object for MySQL database
    """

    #myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    myConnection = pymysql.connect(host="127.0.0.1", port=3306, db="miemie", user="root", password="UCLmiemie2021")
    return myConnection

def getPostgres_modules() -> list:
    """
        Returns list of PostgreSQL module data (all fields)
    """

    con = psycopg2.connect(database=postgre_database, user=postgre_user, host=postgre_host, password=postgre_password, port=postgre_port)
    cur = con.cursor()
    cur.execute("""
        select  id
            ,"Department_Name"
            ,"Department_ID"
            ,"Module_Name"
            ,"Module_ID"
            ,"Faculty"
            ,"Module_Lead"
            ,"Catalogue_Link"
            ,"Description"
            ,"Credit_Value"
            ,"assignedSDG"
            from public."app_module"
    """)
    result = cur.fetchall()
    return result

def create_table() -> None:
    connection = getMySQL()
    cur = connection.cursor()
    cur.execute("""
       CREATE TABLE TestModAssign(
            Module_ID      VARCHAR(150),
            SDG            VARCHAR(150))
    """)
    connection.commit()
    connection.close()

def pushToSQL(module_id: str, data: list) -> None:
    """
        Updates TestModAssign table on MySQL database
    """

    if len(data) != 0:
        connection = getMySQL()
        cur = connection.cursor()
        for i in data:
            insertion = "INSERT INTO TestModAssign (Module_ID, SDG) VALUES (?, ?)"
            cur.execute(insertion, (module_id, i))
        connection.commit()
        connection.close()

def clearTable() -> None:
    """
        Truncates TestModAssign table on MySQL database
    """

    connection = getMySQL()
    cur = connection.cursor()

    command = "TRUNCATE TABLE TestModAssign"
    cur.execute(command)
    connection.commit()
    connection.close()

def progress(count: int, total: int, custom_text: str, suffix='') -> None:
    """
        Visualises progress for a process given a current count and a total count
    """

    bar_len = 60  # size of the progress bar on the commandline
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '*' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
    sys.stdout.flush()

def process_module_LDA_visualisation() -> None:
    """
        Processes module assignments for TestModAssign
    """

    clearTable()
    data = getPostgres_modules()
    counter = 1
    l = len(data)

    for mod in data:
        if mod:
            progress(counter, l, "Writing to TestModAssign")
            counter += 1
            module_result_accumulator = {}
            mod_id = mod[4]
            module_result_accumulator[mod_id] = []
            
            if mod[len(mod) - 1]:
                mod_prediction = mod[len(mod) - 1]['ModelResult'] # str with potential CSV
                if mod_prediction is not None and mod_prediction != None and len(mod_prediction) != 0:
                    if ',' in mod_prediction:
                        temp = mod_prediction.split(',')
                        for i in temp:
                            module_result_accumulator[mod_id].append(int(i))
                    else:
                        module_result_accumulator[mod_id].append(int(mod_prediction))
                pushToSQL(mod_id, module_result_accumulator[mod_id])
    print()


if __name__ == "__main__":
    # create_table()
    process_module_LDA_visualisation()
