# A vetero command implementation, weather quries
# handles weather data using OpenWeatherMap API

from enum import Enum
import debugtools as dbg
import requests
import tempo


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

	# writing all info on stdout (see debug)
	def write(self):
		print("Printing Weather starting at {} (during {}): {}".format(self.start, self.duration, self.desc))
		
		print("Temperature: ", self.temperature)
		print("Precipitation: ", self.precipitation)
		print("Wind: ", self.wind)
		print("Clouds: ", self.clouds)
		print("Sunlight: ", self.sunlight)

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
	
	def write(self):
		print("Weather Info for {} (time +{})".format(self.location, self.timezoneOffset))

		if not self.current is None:
			print("Current: ")
			self.current.write()
		
		if len(self.forecast) > 0:
			print("Forecasts: ")
		
		for info in self.forecast:
			info.write()


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
				data.temperature['real'] = round(mainInfo['temp']) - Weather.ZeroCelsius
			if 'feels_like' in mainInfo:
				data.temperature['feel'] = round(mainInfo['feels_like']) - Weather.ZeroCelsius
			if 'temp_max' in mainInfo:
				data.temperature['maximalReal'] = round(mainInfo['temp_max']) - Weather.ZeroCelsius
			if 'temp_min' in mainInfo:
				data.temperature['minimalReal'] = round(mainInfo['temp_min']) - Weather.ZeroCelsius
		
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



	# returns a WeatherInfo object
	def query(self, locationString, qtype = QueryType.DEFAULT):
		
		location = OWM.parseLocation(locationString)
		if qtype == QueryType.CURRENT or qtype == QueryType.DEFAULT:
			service = "weather"
		else:
			service = "forecast"

		call = "https://{}/data/2.5/{}?{}&appid={}".format(OWM.APIUrl, service, location,OWM.APIKey)
		
		dbg.debug(call)
		
		response = requests.get(call)

		JSON = response.json()
		
		# TODO: modify behaviour

		retcod = JSON['cod']

		if type(retcod) == int:
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

		if 'name' in JSON:
				location = JSON['name']
		

		if 'city' in JSON:
			if 'timezone' in JSON['city']:
				timezoneOffset = JSON['city']['timezone']
			
			if 'name' in JSON['city']:
				location = JSON['city']['name']
		
		if service=="weather":
			# assuming current weather holds for 30 minutes
			current = OWM.readWeatherData(JSON, 30*60)
		
		if service=="forecast":
			if 'list' in JSON:
				forecast = [ OWM.readWeatherData(elem, 3 * 3600) for elem in JSON['list'] ]
		

	
	
		return WeatherInfo(location, None, timezoneOffset, current, forecast)



# definition of the vetero command

from commands import ARG
from commands import CMD

# definitions of arguments:
ArgDict = dict()

def isTime(vals):
	if not ARG.isInt(vals): 
		dbg.debug("Failed int check")
		return False
	t = vals[0]
	if t<-1: return False
	return True

#*Location -- name of the city
ArgDict["loc"] = ARG("loc", ["in"], ARG.isWord, ARG.makeReader(["string"]))
#*Time -- time for which the information is requested, UNIX time, -1 neans now
ArgDict["time"] = ARG("time", ["at", "on"], isTime, ARG.makeReader(["int"]))

# Query aruments specifying type of requested information

# All -- output all available information matching the given time and location 
# (prints the dictionaries of the Weather object) -- for debugging purposes, but prints to stdout
ArgDict["all"] = ARG("all",ARG.noVal, ARG.makeReader([]))

ArgDict["precip"] = ARG("precip", ARG.noVal, ARG.makeReader([]))
# Temperature
ArgDict["temp"] = ARG("temp", ARG.noVal, ARG.makeReader([]))
# Cloudiness 
ArgDict["cloud"] = ARG("cloud", ARG.noVal, ARG.makeReader([]))
# Sunrise and sunset -- available only with time value equals -1
ArgDict["sunrise"] = ARG("sunrise", ARG.noVal, ARG.makeReader([]))
ArgDict["sunset"] = ARG("sunset", ARG.noVal, ARG.makeReader([]))
ArgDict["wind"] = ARG("wind", ARG.noVal, ARG.makeReader([]))

# duration of the timespan in hours that we want to get information about, if not specified 0 is assumed
ArgDict["duration"] = ARG("duration", ARG.isInt, ARG.makeReader(["int"]))

# General description of the weather
ArgDict["desc"] = ARG("desc", ARG.noVal, ARG.makeReader([]))

# definition of the command


def recognize(line):
	return False

def _getValue(dictionary, key):
	if key in dictionary:
		return dictionary[key]
	else:
		return None

# report information from weather (a Weather instance) according to arguments
def reportWeather(weather, arguments, timezoneOffset): 
	dbg.debug("Reporting weather")

	# default value:
	if timezoneOffset is None:
		timezoneOffset = 0
	
	print(tempo.dateTimeToStr(tempo.fromUnixToDateTime(weather.start + timezoneOffset)))

	if 'desc' in arguments and not weather.desc is None:
		print(weather.desc)

	if 'temp' in arguments:
		real = _getValue(weather.temperature, 'real')
		feel = _getValue(weather.temperature, 'feel')
		tmax = _getValue(weather.temperature, 'maximalReal')
		tmin = _getValue(weather.temperature, 'minimalReal')
		
		msg = ""
		if not real is None:
			msg = "temperature: {}\u2103".format(real)
			if not feel is None:
				msg = msg + " (feels like {}\u2103)".format(feel)
			if not tmin is None and not tmax is None:
				msg = msg + ", between {}\u2103 and {}\u2103".format(tmin, tmax)
			
		elif not feel is None:
			msg = "perceived temperature: {}\u2103".format(feel)

			if not tmin is None and not tmax is None:
				msg = msg + ", real between {}\u2103 and {}\u2103".format(tmin, tmax)
		elif not tmin is None and not tmax is None:
				msg = "temperature between {}\u2103 and {}\u2103".format(tmin, tmax)
		
		if len(msg)>0:
			print(msg)
		
	if 'precip' in arguments:
		rain = ""
		snow = ""
		if 'rainVolume' in weather.precipitation:
			rain = "rain volume {}mm".format(weather.precipitation['rainVolume'])
		if 'snowVolume' in weather.precipitation:
			snow = "snow volume {}mm".format(weather.precipitation['snowVolume'])
		
		msg = rain
		if len(msg)>0 and len(snow)>0:
			msg = msg + ", " + snow
		
		if len(msg)>0:
			print(msg)
		else:
			print("no precipitation")
		
	if 'cloud' in arguments and 'cloudiness' in weather.clouds:
		print("cloudiness equal {}%".format(weather.clouds['cloudiness']))

	if 'wind' in arguments and 'speed' in weather.wind:
		print("wind speed: {} m/s".format(weather.wind['speed']))

	daylightmsg = ""
	sunrise = None
	sunset = None
	if 'sunrise' in arguments and 'sunrise' in weather.sunlight:
		sunriseTime = tempo.fromUnixToDateTime(weather.sunlight['sunrise'] + timezoneOffset)
		sunrise = tempo.timeToStr(sunriseTime.time())
	if 'sunset' in arguments and 'sunset' in weather.sunlight:
		sunsetTime = tempo.fromUnixToDateTime(weather.sunlight['sunset'] + timezoneOffset)
		sunset = tempo.timeToStr(sunsetTime.time())
	
	if not sunrise is None and not sunset is None:
		print("The sun will rise at {} and set at {}.".format(sunrise, sunset))
	elif not sunset is None:
		print("The sun will set at {}.".format(sunset))
	elif not sunrise is None:
		print("The sun will rise at {}.".format(sunrise))


def execute(session, arguments):

	dbg.debug("Executing vetero with args: ", arguments)

	if session.weather is None:
			dbg.debug("Setting a new weather API manager")
			session.weather = OWM()
	

	# modify the following lines when implementing new types of queries
	if arguments["time"][0]==-1: qType = QueryType.CURRENT
	else: qType = QueryType.SHORTFORECAST

	locationString = "q={}".format(arguments["loc"][0])

	wInfo = session.weather.query(locationString, qtype = qType)

	# just print the whole information on stdout
	if "all" in arguments:
		wInfo.write()
		return True

	print("{}:".format(wInfo.location))



	# reporting the current state of weather
	if arguments["time"][0]==-1:
		if not wInfo.current is None:
			reportWeather(wInfo.current, arguments, wInfo.timezoneOffset)
	
	# reporing forecasts
	if arguments["time"][0]>=0 or 'duration' in arguments:

		if arguments["time"][0]==-1:
			timeBegin = tempo.getCurrentTimestamp()
		else:
			timeBegin = arguments["time"][0]
		
		timeEnd = timeBegin

		if 'duration' in arguments:
			timeEnd += arguments['duration'][0] * 60 * 60
		
		for fc in wInfo.forecast:
			if max(timeBegin, fc.start)<=min(timeEnd, fc.start+fc.duration):
				reportWeather(fc, arguments, wInfo.timezoneOffset)



	#executed successfuly
	return True


Vetero = CMD("vetero", ArgDict, CMD.compulsoryArgs(["loc", "time"]), execute, recognize = None)

# for testing

if __name__ == "__main__":
	
	API = OWM()

	#current = API.query("q=Meghalaya", QueryType.CURRENT)
	#forecast = API.query("q=Meghalaya", QueryType.LONGFORECAST)
	#current.debug()
	#forecast.debug()