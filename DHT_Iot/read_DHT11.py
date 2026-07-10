import board
import adafruit_dht

sensor = adafruit_dht.DHT11(board.D4)

def read_dht11():
	temperature = sensor.temperature
	humidity = sensor.humidity
	if humidity is not None and temperature is not None:
		return round(temperature, 1), round(humidity, 1)
	else:
		print("Failed to read sensor")
	return None, None

if __name__ == "__main__":
	temp, hum = read_dht11()
	if temp:
		print(f"Temperature: {temp}C, Humidity: {hum}%")
