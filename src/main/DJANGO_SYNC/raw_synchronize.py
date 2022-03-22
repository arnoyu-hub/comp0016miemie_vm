from main.CONFIG_READER.read import get_details
import pymysql
import pymongo
import psycopg2
import pyodbc
import json
import sys

class RawSynchronizer():
    
    def __init__(self):
        self.server = get_details("SQL_SERVER", "client")
        self.database = get_details("SQL_SERVER", "database")
        self.username = get_details("SQL_SERVER", "username")
        self.password = get_details("SQL_SERVER", "password")
        self.driver = get_details("SQL_SERVER", "driver")

        self.postgre_database = get_details("POSTGRESQL", "database")
        self.postgre_user = get_details("POSTGRESQL", "username")
        self.postgre_host = get_details("POSTGRESQL", "host")
        self.postgre_password = get_details("POSTGRESQL", "password")
        self.postgre_port = get_details("POSTGRESQL", "port")

        self.host = get_details("MONGO_DB", "client")

    def __progress(self, count: int, total: int, custom_text: str, suffix='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %
                         (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __get_mysql_module_data(self) -> list:
        """
            Gets the list of all modules and their data from the MySQL database
        """

        #myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=3306;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        myConnection = pymysql.connect(host="127.0.0.1", port=3306, db="miemie", user="root", password="UCLmiemie2021")
        curr = myConnection.cursor()
        curr.execute("SELECT * FROM moduledata")
        return curr.fetchall()

    def __update_module_from_mysql(self) -> None:
        """
            Updates the PostgreSQL database with module data from the MySQL database
        """

        data = self.__get_mysql_module_data()
        con = psycopg2.connect(database=self.postgre_database, user=self.postgre_user, host=self.postgre_host, password=self.postgre_password, port=self.postgre_port)
        cur = con.cursor()
        c = 1
        for i in data:
            self.__progress(c, len(data), "Syncing scraped modules to Django")
            query = """INSERT INTO public.app_module (Department_Name,Department_ID,Module_Name,Module_ID,Faculty,Credit_Value,Module_Lead,Catalogue_Link,Description)
                       VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}') ON CONFLICT (Module_ID) DO NOTHING""".format(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8])
            query2 = """INSERT INTO public.app_moduleha (Department_Name,Department_ID,Module_Name,Module_ID,Faculty,Credit_Value,Module_Lead,Catalogue_Link,Description)
                       VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}') ON CONFLICT (Module_ID) DO NOTHING""".format(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8])
            con.commit()
            c += 1
        cur.close()
        print()

    def __update_publications_from_mongo(self) -> None:
        """
            Updates PostgreSQL with publication data from MongoDB
        """

        client = pymongo.MongoClient(self.host)
        db = client.Scopus
        col = db.Data
        data = col.find(batch_size=10)

        con = psycopg2.connect(database=self.postgre_database, user=self.postgre_user, host=self.postgre_host, password=self.postgre_password, port=self.postgre_port)
        cur = con.cursor()

        blank_dict = {
            '1': '', '2': '', '3': '', '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': '', '10': '', '11': '', '12': '',
            '13': '', '14': '', '15': '', '16': '', '17': '', '18': '',
            'DOI': '',
            'IHE': [],
            'SVM': [],
            'Title': '',
            'Validation': {
                'ColorRed': 0, 'ColorBlue': 0, 'ColorGreen': 0, 'Similarity': 0,
                'StringCount': [['1', 0.0], ['2', 0.0], ['3', 0.0], ['4', 0.0], ['5', 0.0], ['6', 0.0],
                    ['7', 0.0], ['8', 0.0], ['9', 0.0], ['10', 0.0], ['11', 0.0], ['12', 0.0],
                    ['13', 0.0], ['14', 0.0], ['15', 0.0], ['16', 0.0], ['17', 0.0], ['18', 0.0]],
                'SDG_Keyword_Counts': []
                },
            'ModelResult': '',
            'StringResult': '',
            'IHE_Prediction': '',
            'SVM_Prediction': ''
        }
        
        blank_dict2 = {
            '1': '', '2': '', '3': '', '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': '', '10': '', '11': '', '12': '',
            '13': '', '14': '', '15': '', '16': '', '17': '', '18': '',
            'DOI': '',
            'IHE': [],
            'SVM': [],
            'Title': '',
            'Validation': {
                'ColorRed': 0, 'ColorBlue': 0, 'ColorGreen': 0, 'Similarity': 0,
                'StringCount': [['1', 0.0], ['2', 0.0], ['3', 0.0], ['4', 0.0], ['5', 0.0], ['6', 0.0],
                    ['7', 0.0], ['8', 0.0], ['9', 0.0], ['10', 0.0], ['11', 0.0], ['12', 0.0],
                    ['13', 0.0], ['14', 0.0], ['15', 0.0], ['16', 0.0], ['17', 0.0], ['18', 0.0]],
                'HA_Keyword_Counts': []
                },
            'ModelResult': '',
            'StringResult': '',
            'IHE_Prediction': '',
            'SVM_Prediction': ''
        }
        
        c, l = 0, 90000
        for i in data:
            self.__progress(c, l, "Syncing scraped publications to Django")
            del i['_id']
            doi = i['DOI'].replace("\'", "\'\'")
            title = i['Title'] = i['Title'].replace("\'", "\'\'")

            cur.execute("SELECT exists (SELECT 1 FROM public.app_publication WHERE doi = \'{}\')".format(doi))
            existing_pub = cur.fetchone()[0]

            if not existing_pub:
                if i['Abstract']:
                    i['Abstract'] = i['Abstract'].replace("\'", "\'\'")
                if i['Source']:
                    i['Source'] = i['Source'].replace("\'", "\'\'")
                if i['AuthorData']:
                    for key, val in i['AuthorData'].items():
                        if val['Name']:
                            val['Name'] = val['Name'].replace("\'", "\'\'")
                        if val['AffiliationName']:
                            val['AffiliationName'] = val['AffiliationName'].replace("\'", "\'\'")
                if i['IndexKeywords']:
                    for index, val in enumerate(i['IndexKeywords']):
                        i['IndexKeywords'][index] = val.replace("\'", "\'\'")
                if i['AuthorKeywords']:
                    for index, val in enumerate(i['AuthorKeywords']):
                        i['AuthorKeywords'][index] = val.replace("\'", "\'\'")
                #query = """INSERT INTO public.app_publication (title, data, \"assignedSDG\", doi) SELECT '{0}', '{1}', '{2}', '{3}'  WHERE NOT EXISTS (SELECT 1 FROM public.app_publication WHERE doi='{3}')""".format(title, json.dumps(i), json.dumps(blank_dict), doi)
                query = """INSERT INTO public.app_publication (title, data, \"assignedSDG\", doi) VALUES ('{0}', '{1}', '{2}', '{3}') ON CONFLICT (id) DO NOTHING""".format(title, json.dumps(i), json.dumps(blank_dict),doi)
                query2 = """INSERT INTO public.app_publicationha (title, data, \"assignedHA\", doi) VALUES ('{0}', '{1}', '{2}', '{3}') ON CONFLICT (doi) DO NOTHING""".format(title, json.dumps(i), json.dumps(blank_dict2),doi)
                cur.execute(query)
                #cur.execute(query2)#id
                con.commit()
            c += 1
        print()
        client.close()
        con.close()

    def run(self):
        #self.__update_module_from_mysql()
        self.__update_publications_from_mongo()
