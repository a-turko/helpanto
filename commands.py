# definitions of command classes
# module for command recognition from natural language will be added here

# class for representing an argument
class ARG:
	def __init__(self, name, indicators, validate, read):
		self.name = name
		self.indicators = indicators	# indicators for command recognition
		self.validate = validate		# procedure for checking whether the value is valid
		self.read = read				# read values of the arguments from tokens, takes list of tokens as argument
										# returns the number of tokens read

	# creates a read procedure for a list of values with types specified by valTypes
	# returns a list of values
	@staticmethod
	def makeReader(valTypes):
		def reader(values, start):
			ret = []
			assert(start + len(valTypes) <= len(values))
			for i,valType in enumerate(valTypes):
				if valType=="int":
					ret.append(int(values[start+i]))
				if valType=="float":
					ret.append(float(values[start+i]))
				if valType=="string":
					ret.append(str(values[start+i]))
			
			return ret
		
		return reader
	
	# validator that checks whether value is empty
	@staticmethod
	def noVal(value):
		return len(value)==0

				
			

# class for representing a command
class CMD:
	
	# try to recognize the command from the line, returns:
	# a dictionary with recognized arguments in case of success
	# None in case of failure
	# TODO: implement
	@staticmethod
	def recognition(self, line):
		return None


	# creates a simple procedure for validation, which checks
	# whether all the arguments from argList are present in ArgDict
	@staticmethod
	def compulsoryArgs(argList):
		def validator(argDict):
			for arg in argList:
				if not arg in argDict: return False
			return True
		return validator

	def __init__(self, name, arguments, validate, execute, recognize = None):
		
		# default values:
		if recognize is None: recognize = CMD.recognition

		self.name = name
		self.arguments = arguments		# dictionary with ARG objects by name
		self.validate = validate		# procedure foor checking validity of argument
										# takes a dictionary with entries argname:argval

		self.execute = execute			# procedure for executing a command, takes a Session object as an argument
										# execute procedure takes a Session object and a dictionary with arguments

		self.recognize =  recognize		# recognizes the command and its arguments from natural language, returns
										# dictionary with arguments in case of success and None in case of failure

	# checks whether the token is a name of a option proceeded by '--'
	# if it's not returns None, and right ARG otherwise
	def option (self, token):
		if len(token)<3 or token[0]!='-' or token[1]!='-': return None
		option = token.lstrip('-')
		if option in self.arguments: return self.arguments[option]
		else: return None

	# procedure for parsing a properly structured command:
	# takes a list of tokens as argument, returns a dictionary
	# with recognized options, None if 
	def parse(self, tokens):
		if len(tokens)==0 or tokens[0]!=self.name:
			# it's a wrong command
			return None
		
		argumentDict = dict()
		i = 1
		while i <len(tokens):
			token = tokens[i]
			i+=1
			argument = self.option(token)
			if argument is None:
				continue
			
			vals = argument.read(tokens, i)
			i+=len(vals)

			if argument.validate(vals):
				argumentDict[argument.name] = vals
			
		return argumentDict
	

	

	
	
