# Imports 📥

# Importar librería para la conexión con MySQL
# -----------------------------------------------------------------------
import mysql.connector
from mysql.connector import errorcode


# Importar librerías para manipulación y análisis de datos
# -----------------------------------------------------------------------
import pandas as pd

class CreateDatabase:
    def __init__(self, user, password, host, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self, database=None):
        try:
            # Establish the connection to the database
            self.connection = mysql.connector.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                database=database
            )
            # Create the cursor after establishing the connection
            self.cursor = self.connection.cursor()
            print(f"Connection to database '{database or 'server'}' established successfully")
        except mysql.connector.Error as err:
            print(f'Connection error: {err}')

    def create_database(self):
        try:
            # Connect without specifying a database
            self.connect(database=None)
            # Check the connection status
            if self.connection.is_connected():
                print("Temporary connection to server established for database creation.")
            else:
                print("Temporary connection to server failed.")
                return

            # Create the database using the provided name
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"Database '{self.database}' created or already exists.")
        except mysql.connector.Error as err:
            print(f'Error creating database: {err}')
        finally:
            # Close the temporary connection
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                print("Temporary connection closed.")
        
        # Reconnect to the new database
        self.connect(database=self.database)
        # Check the connection status again
        if self.connection.is_connected():
            print(f"Connection to database '{self.database}' re-established.")
        else:
            print(f"Connection to database '{self.database}' failed.")

    def create_table(self, table_name, schema):
        try:
            # Create a table using the provided name and schema
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            print(f"Table '{table_name}' created or already exists.")
        except mysql.connector.Error as err:
            print(f'Error creating table: {err}')

    def insert_data(self, query, values):
        try:
            # Execute the query with the proportioned values
            self.cursor.execute(query, values)
            self.connection.commit()  # confirm the values and commit
            print(f"{self.cursor.rowcount} record(s) inserted.")

        except mysql.connector.Error as err:
            print(f'Error inserting data: {err}')
            print("Error Code:", err.errno)
            print("SQLSTATE:", err.sqlstate)
            print("Message:", err.msg)

    def bulk_insert_data(self, dataframe, table_name):
        placeholders = ", ".join(["%s"] * len(dataframe.columns))
        columns = ", ".join(dataframe.columns)
        update_clause = ", ".join([f"{col}=VALUES({col})" for col in dataframe.columns])
        query = f"""
        INSERT INTO {table_name} ({columns}) VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
        """

        for row in dataframe.itertuples(index=False, name=None):
            self.insert_data(query, row)

            
    def close(self):
        # Close cursor and connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")