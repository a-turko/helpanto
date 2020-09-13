# helpanto: main helpanto source file

import debugtools as dbg
from lingvoy import Lingvoy
from vetero import Vetero
import commands

# List of available commands:

CMDList = [Lingvoy, Vetero]

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
		
		tokens = cut[1:]

		# CMD MODE
		if cut[0]=='>':
			command = None
			for cmd in CMDList:
				argDict = cmd.parse(tokens)
				if not argDict is None:
					if not cmd.validate(argDict):
						dbg.debug("Command arguments not valid: ", argDict)
						continue

					command = cmd
					arguments = argDict

			

			#print(command.validate)

			
			
		# command recognition mode
		else:

			command  = None
			for cmd in CMDList:
				argDict = cmd.regonize(line)
				
				if argDict is None:
					continue
				command = cmd
				arguments = argDict


		if command is None:
				dbg.debug("No command rezognized")
				return -1
		
		retcode = command.execute(self, arguments)
		return retcode
	

		dbg.debug("Unsupported mode")
		return -1
		



if __name__=="__main__":

	dbg.debug(Lingvoy.keywords)
	dbg.debug(Vetero.keywords)

	session = Session()
	print("Avaiting commands")



	while True:
		line = input()
		if line.rstrip()=="exit": break
		session.react(line)
