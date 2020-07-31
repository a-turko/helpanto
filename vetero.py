# vetero -- a weather data module
# handles weather data using OpenWeatherMap API guide

from enum import Enum
import debugtools as dbg
import requests


# data about the weather for a period of time
class Weather:
	ZeroCelsius = 273
	def __init__(self, start, duration, desc = None):

		self.start = start							# UNIX time (in UTC)
		self.duration = duration					# in seconds
		self.desc = desc							# weather description i.e. "storm"
		self.temperature = dict()					# information about temperature
		self.precipitation = dict()					# information about temperature
		self.wind = dict()							# information about wind
		self.clouds = dict()						# information about clouds, fog etc.
		self.sunlight = dict()						# information about sunset, sunrice

		# Any keys in the dictionaries may not be present
		# temperature (data: ints in celsius): real, feel, maximal, minimal, morn, even, day, night
		# (last for in real and feel variants: maximalFeel, mornReal etc.)
		# precipitation: rainChance, rainVolume (in mm), snowChance, snowVolume (in mm)
		# wind: speed (in m/s)
		# clouds: cloudiness (in %)
		# sunlight: sunrise (UNIX time), sunset (UNIX time)

	# for debugging -- display all info
	def debug(self):
		dbg.debug("Printing Weather starting at {} (during {}): {}".format(self.start, self.duration, self.desc))
		
		dbg.debug("Temperature: ", self.temperature)
		dbg.debug("Precipitation: ", self.precipitation)
		dbg.debug("Wind: ", self.wind)
		dbg.debug("Clouds: ", self.clouds)
		dbg.debug("Sunlight: ", self.sunlight)

class WeatherInfo:
	def __init__(self, location = None, timezone = None, \
		timezoneOffset = None, current = None, forecast = []):
		self.location = location					# name of the city
		self.timezone = timezone
		self.timezoneOffset = timezoneOffset		# shift in seconds from UTC
		self.current = current						# a Weather object
		self.forecast = forecast 					# list of Weather objects

	def debug(self):
		dbg.debug("Weather Info for {} (time +{})".format(self.location, self.timezoneOffset))

		if not self.current is None:
			dbg.debug("Current: ")
			self.current.debug()
		
		if len(self.forecast) > 0:
			dbg.debug("Forecasts: ")
		
		for info in self.forecast:
			info.debug()


# type of weather queries
class QueryType(Enum):
	DEFAULT = 0
	CURRENT = 1
	SHORTFORECAST = 2
	LONGFORECAST = 3

# handling queries to OpenWeatherMap
class OWM:
	APIKey = "84825fbd278aa312f2f3d1b35db5fb98"
	APIUrl = "api.openweathermap.org"

	# TODO: implement
	# parsing location string to appropriate format for the https request
	@staticmethod
	def parseLocation(locationString):
		return locationString
	
	# reads data from answers to "forecast" and "weather" API queries
	@staticmethod
	def readWeatherData(JSON, duration):
		start = JSON['dt']
		weatherSection = JSON['weather']
		desc = ""
		for entry in weatherSection:
			if 'description' in entry:
				if len(desc) > 0:
					desc = desc + "; "
				desc = desc + entry['description']
		
		data = Weather(start, duration, desc)

		if 'clouds' in JSON:
			cloudInfo = JSON['clouds']
			if 'all' in cloudInfo:
				data.clouds['cloudiness'] = cloudInfo['all']

		if 'main' in JSON:
			mainInfo = JSON['main']
			if 'temp' in mainInfo:
				data.temperature['real'] = mainInfo['temp'] - Weather.ZeroCelsius
			if 'feels_like' in mainInfo:
				data.temperature['feel'] = mainInfo['feels_like'] - Weather.ZeroCelsius
			if 'temp_max' in mainInfo:
				data.temperature['maximalReal'] = mainInfo['temp_max'] - Weather.ZeroCelsius
			if 'temp_min' in mainInfo:
				data.temperature['minimalReal'] = mainInfo['temp_min'] - Weather.ZeroCelsius
		
		if 'wind' in JSON:
			windInfo = JSON['wind']
			if 'speed' in windInfo:
				data.wind['speed'] = windInfo['speed']
		
		if 'rain' in JSON:
			for key in JSON['rain']:
				if key=='1h' or key=='3h':
					data.precipitation['rainVolume'] = JSON['rain'][key]
		
		if 'snow' in JSON:
			for key in JSON['snow']:
				if key=='1h' or key=='3h':
					data.precipitation['snowVolume'] = JSON['snow'][key]
			

		if 'sys' in JSON:
			sysInfo = JSON['sys']
			if 'sunrise' in sysInfo:
				data.sunlight['sunrise'] = sysInfo['sunrise']
			if 'sunset' in sysInfo:
				data.sunlight['sunset'] = sysInfo['sunset']
		
		return data



	# returns the WeatherInfo element
	def query(self, locationString, type = QueryType.DEFAULT):
		
		location = OWM.parseLocation(locationString)
		if type == QueryType.CURRENT or type == QueryType.DEFAULT:
			service = "weather"
		else:
			service = "forecast"

		call = "https://{}/data/2.5/{}?{}&appid={}".format(OWM.APIUrl, service, location,OWM.APIKey)
		
		dbg.debug(call)
		
		response = requests.get(call)

		JSON = response.json()
		
		# TODO: modify behaviour

		retcod = JSON['cod']

		if retcod is int:
			code = retcod
		else:
			code = int(retcod)

		if code != 200:
			dbg.callErr(do_quit = False, msg = "Failed to retrieve API answer")
			return
		
		# Read the weather data

		

		current = None
		forecast = []
		location = None
		timezoneOffset = None

		if 'timezone' in JSON:
			timezoneOffset = JSON['timezone']
		
		if service=="weather":
			if 'name' in JSON:
				location = JSON['name']
			
			# assuming current weather holds for 30 minutes
			current = OWM.readWeatherData(JSON, 30*60)
		
		if service=="forecast":
			if 'city' in JSON and 'name' in JSON['city']:
				location = JSON['city']['name']

			if 'list' in JSON:
				forecast = [ OWM.readWeatherData(elem, 3 * 3600) for elem in JSON['list'] ]
		

	
	
		return WeatherInfo(location, None, timezoneOffset, current, forecast)



# definition of the vetero command

import commands

# definitions of arguments:


# definition of the command

def validate(arguments):
	return True

def parse(line):
	return

def recognize(line):
	return False

def execute(session, arguments):
	return



		

# for testing

if __name__ == "__main__":
	
	API = OWM()

	current = API.query("q=Meghalaya", QueryType.CURRENT)
	forecast = API.query("q=Meghalaya", QueryType.LONGFORECAST)

	current.debug()

	forecast.debug()





		