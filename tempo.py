# tempo -- time and date module
import debugtools as dbg
import datetime
import time

# in (UTC)
Epoch = datetime.datetime(year=1970, month = 1, day=1)

# takes Unix timestamp as input and returns a timedate object
# does not take timezones into consideration
def fromUnixToDateTime(unx):

	delta = datetime.timedelta(seconds=unx)
	return Epoch + delta

# return the current Unix timestamp
def getCurrentTimestamp():
	return int(time.time())

# returns a string representing time (hour and minues)
def timeToStr(t):
	return " {:02d}:{:02d}".format(t.hour, t.minute)
# returns a string representing date and time with precision of one minute
def dateTimeToStr(d):
	return d.date().isoformat() + " {:02d}:{:02d}".format(d.hour, d.minute)



if __name__ == "__main__":

	timestamp = time.time()

	dt = fromUnixToDateTime(timestamp)

	print(dt)

	t = dt.time()

	print(type(t), t)