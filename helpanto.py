# helpanto: main helpanto source file

import debugtools
import lingvoy
import vetero 


# class for handling a user session
class Session:

	def __init__(self):
		self.dataContext = [] 			# list of objects with information fetched so far
		self.weather = None
		self.languages = None
	
	# reacts for a line from user, works in modes:
	# CMD mode (well structured commands): > CMD ARGS...
	def react(self, line):
		cut = line.split()
		if len(cut)==0:
			# no reaction to an empty line
			return 0
		
		# CMD MODE
		if cut[0]=='>':
			
		
