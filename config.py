# config.py
import urllib

class Config:
    server = 'localhost'
    database = 'Evangelio'
    driver = 'ODBC Driver 17 for SQL Server'

    connectionString = (
        f"mssql+pyodbc:///?odbc_connect=" +
        urllib.parse.quote_plus(
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        )
    )
