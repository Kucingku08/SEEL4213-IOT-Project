import sqlite3

# Create database file
conn = sqlite3 . connect ('sensor_data .db ')
cursor = conn . cursor ()
# Create table
cursor . execute ( '''
CREATE TABLE IF NOT EXISTS readings (
id INTEGER PRIMARY KEY AUTOINCREMENT ,
timestamp TEXT NOT NULL ,
temperature REAL NOT NULL ,
humidity REAL NOT NULL )
''')
conn . commit ()
conn . close ()
