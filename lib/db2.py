import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
host = "/cloudsql/" + cloud_sql_connection_name

#conn = psycopg2.connect(database=db_name, user = db_user, password = db_pass, host = "/cloudsql/" + cloud_sql_connection_name)
dbConnection = "dbname=" + db_name + ' user=' + db_user + ' host=' + host + ' password=' + db_pass
connectionpool = SimpleConnectionPool(1, 10, dsn=dbConnection)


@contextmanager
def getcursor():
    con = connectionpool.getconn()
    try:
        yield con.cursor()
        con.commit()
    finally:
        connectionpool.putconn(con)


with getcursor() as cur:
    cur.execute(
            "CREATE TABLE IF NOT EXISTS data "
            "( athlete_id TEXT, unfin TEXT, finished TEXT, MTS TEXT, polylines TEXT, PRIMARY KEY (athlete_id) );"
        )

# Make a convenience function for running SQL queries
def sql_query(query):
    with getcursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return rows

def sql_edit_insert(query,var):
    with getcursor() as cur:
        cur.execute(query,var)


def sql_delete(query,var):
    with getcursor() as cur:
        cur.execute(query,var)

def sql_query2(query,var):
    with getcursor() as cur:
        cur.execute(query,var)
        rows = cur.fetchall()
    return rows


