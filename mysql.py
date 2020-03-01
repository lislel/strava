import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(user="lauren",
                                  password="password",
                                  host="localhost",
                                  database="strava_data")

    cursor = connection.cursor()

    create_table_query = '''CREATE TABLE data
          (athlete_id TEXT, unfin TEXT, fin TEXT, MTS TEXT, polylines TEXT ); '''

    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

except (Exception, psycopg2.DatabaseError) as error:
    print("Error while creating PostgreSQL table", error)
finally:
    # closing database connection.
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")