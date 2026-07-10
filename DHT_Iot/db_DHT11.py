import os, time, logging, sqlite3, board
from datetime import datetime
import adafruit_dht
# Configuration
SENSOR = adafruit_dht.DHT11(board.D4)
DB_FILE = "sensor_data.db"
def init_database():
	""" Initialize database schema """
	conn = sqlite3.connect(DB_FILE)
	cursor = conn.cursor()
	cursor.execute( '''
		CREATE TABLE IF NOT EXISTS readings (
		id INTEGER PRIMARY KEY AUTOINCREMENT ,
		timestamp TEXT NOT NULL ,
		temperature REAL NOT NULL ,
		humidity REAL NOT NULL )
		''')
	conn.commit()
	conn.close()

def read_dht11 (retries =5, delay =2.0) :
	""" Read temperature and humidity from DHT11 sensor """
	for i in range (retries) :
		humidity, temperature = SENSOR.humidity, SENSOR.temperature
	if humidity is not None and temperature is not None :
		return round(temperature, 1), round(humidity, 1)
	logging.warning(f" DHT11 read failed ( attempt {i +1}/{ retries })")
	time.sleep(delay)
	raise RuntimeError(" DHT11 sensor not responding ")

def save_reading (temperature, humidity) :
	""" Save sensor reading to database """
	conn = sqlite3.connect(DB_FILE)
	cursor = conn.cursor()
	timestamp = datetime.now().isoformat()
	cursor.execute (
		" INSERT INTO readings ( timestamp , temperature , humidity ) VALUES (? , ? , ?)",(timestamp, temperature, humidity )
	)
	conn.commit()
	conn.close ()
	logging.info(f" Saved : { temperature }C, { humidity }% at { timestamp }")

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	init_database()

	try:
		temp, hum = read_dht11()
		print(f"Temperature: {temp}C, Humidity: {hum}%")
		save_reading(temp, hum)
		print("Data saved to database!")
	except Exception as e:
		print(f"Error: {e}")
