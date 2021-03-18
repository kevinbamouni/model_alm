import sqlite3
from sqlite3 import Error
import os
import pandas as pd


def create_connection(db_file):
    """ create a database connection to a SQLite database 
    :param db_file :database path file
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print('SQLITE version : '+ sqlite3.version + ' creation et connection à la base de données OK!')
    except Error as e:
        print(e)
    return conn


def create_run(conn, project):
    """
    Create a new project into the projects table
    :param conn:
    :param run:
    :return: project id
    """
    sql = ''' INSERT INTO runs(begin_time,end_time,comment)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    #return cur.lastrowid


# if __name__ == '__main__':
def database_iinit():
    # print(os.path.abspath(os.curdir)) permet de recupérer le current directory / en vrai je ne comprends pas le code
    sqliteconn = create_connection(os.path.abspath(os.curdir) + "/database/pythonsqlite.db")
    cursor = sqliteconn.cursor()

    with open('/Users/kevinbamouni/OneDrive/Modele_ALM/run_tools/create_table_run.sql', 'r') as sqlite_file:
        sql_script = sqlite_file.read()

    cursor.executescript(sql_script)
    print("SQLite : Database initialisation script has been executed successfully")

    #df = pd.read_csv(os.path.abspath(os.curdir) + "/output_test_data/mp_global_projection.csv", sep=",")
    #df.to_sql('passifres', con=sqliteconn)

    # close connection et cursor connection
    cursor.close()
    sqliteconn.close()