import os
import psycopg2

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

conn = psycopg2.connect(database=db_name, user = db_user, password = db_pass, host = "/cloudsql/" + cloud_sql_connection_name)
curr = conn.cursor()
curr.execute(
        "CREATE TABLE IF NOT EXISTS data "
        "( athlete_id TEXT, unfin TEXT, finished TEXT, MTS TEXT, polylines TEXT, PRIMARY KEY (athlete_id) );"
    )

# Make a convenience function for running SQL queries
def sql_query(query):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows

def sql_edit_insert(query,var):
    cur = conn.cursor()
    cur.execute(query,var)
    conn.commit()

def sql_delete(query,var):
    cur = conn.cursor()
    cur.execute(query,var)

def sql_query2(query,var):
    cur = conn.cursor()
    cur.execute(query,var)
    rows = cur.fetchall()
    return rows


