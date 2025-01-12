import pyodbc


class DatabaseConnection:
    def __init__(self, server, port, database, user, password):
        self.connection_string = (
            f"DRIVER={{FreeTDS}};SERVER={server};PORT={port};DATABASE={database};UID={user};PWD={password};TDS_Version=5.0"
        )
        self.connection = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(self.connection_string)
            print("Conexión exitosa a la base de datos.")
        except pyodbc.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise

    def execute_query(self, query, params=None):
        if self.connection is None:
            raise Exception("Primero debes conectar a la base de datos.")
        cursor = self.connection.cursor()
        cursor.execute(query, params or [])
        return cursor.fetchall()

    def close(self):
        if self.connection:
            self.connection.close()
            print("Conexión cerrada.")
