import pyodbc
import pymysql
from main.CONFIG_READER.read import get_details

class Create_ModuleData():
    def __init__(self):
        self.server = get_details("SQL_SERVER", "client")
        self.database = get_details("SQL_SERVER", "database")
        self.username = get_details("SQL_SERVER", "username")
        self.password = get_details("SQL_SERVER", "password")
        self.driver = get_details("SQL_SERVER", "driver")

    def create(self):
        """
            Instantiates MySQL Database Table <ModuleData>
        """

       # myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=3306;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        myConnection = pymysql.connect(host="127.0.0.1", port=3306, db="miemie", user="root", password="UCLmiemie2021")
        cur = myConnection.cursor()

        create = """CREATE TABLE moduledata(
                        Department_Name      VARCHAR(150),
                        Department_ID        VARCHAR(150),
                        Module_Name          VARCHAR(150),
                        Module_ID            VARCHAR(150) PRIMARY KEY,
                        Faculty              VARCHAR(100),
                        Credit_Value         FLOAT,
                        Module_Lead          VARCHAR(100),
                        Catalogue_Link       TEXT(16383),
                        Module_Description          TEXT(16383),
                        Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP
                    );"""

        cur.execute(create)
        myConnection.commit()
        myConnection.close()
