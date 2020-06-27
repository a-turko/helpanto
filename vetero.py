# vetero -- a weather data module
# handles weather data using OpenWeatherMap API guide

import debugtools as dbg
import requests

# data about the weather for a period of time
class Wheather:
	def __init__(start, duration, temperatureReal = None, temperatureFeel = None, \
		windSpeed = None, rainChance = None, rainVolume = None, snowChance = None, \
		snowVolume = None, cloudiness = None):

		self.start = start							# UNIX time (int UTC)
		self.duration = duration					# in seconds
		self.temperatureReal = temperatureReal		# real temperature in Celsius
		self.temperatureFeel = temperatureFeel		# feels like temperature in Celsius
		self.windSpeed = windSpeed					# wind speed in m/s
		self.rainChance = rainChance
		self.rainVolume = rainVolume				# rain volume in mm for the given period of time
		self.snowChance = snowChance
		self.snowVolume = snowVolume
		self.cloudiness = cloudiness				# cloudiness in %


class WeatherForcast:
	def __init__(location = None, sunrise = None, sunset = None, timezone = None, data = []):
		self.location = location					# name of the city
		self.sunrise = sunrise						# UNIX time
		self.sunset = sunset						# UNIX time
		self.timezone = timezone					# shift in seconds from UTC
		self.data = data 							# list of Weather objects


# handling queries to OpenWeatherMap
class OWM:
	APIKey = "84825fbd278aa312f2f3d1b35db5fb98"
	APIUrl = "api.openweathermap.org"

	getForcast(city, contryCode = None):
		if countryCode is None:
			location = city
		else:
			location = "{},{}".format(city, countryCode)
		
		call = "{url}/data/2.5/forecast?q={loc}&appid={apiKey}".format(APIUrl, location,APIKey)

		response = requests.get(call)

		JSON = response.json()

		