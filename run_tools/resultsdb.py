import sqlite3
from sqlite3 import Error
import os
import pandas as pd



def create_connection(db_file):
    """ create a database connection to a SQLite database 
    :param db_file: database path file
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print('SQLITE version : '+ sqlite3.version + ' creation et connection à la base de données OK!')
    except Error as e:
        print(e)
    return conn



if __name__ == '__main__':
    # print(os.path.abspath(os.curdir)) permet de recupérer le current directory / en vrai je ne comprends pas le code
    conn = create_connection(os.path.abspath(os.curdir) + "/database/pythonsqlite.db")

    df = pd.read_csv(os.path.abspath(os.curdir) + "/output_test_data/mp_global_projection.csv", sep=",")
    df.to_sql('passifres', con=conn)

    conn.close()