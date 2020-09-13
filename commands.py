
import debugtools as dbg
import re

# definitions of command classes
# module for command recognition from natural language will be added here

# class for representing an argument
class ARG:
	def __init__(self, name, validate, read):
		self.name = name
		self.validate = validate		# procedure for checking whether the value is valid
		self.read = read				# read values of the arguments from tokens, takes list of tokens as argument
										# returns the number of tokens read
		self.hasRecognitionData = False # true iff the instance has valueAliases, indicators and contextScanners

	# valueAliases is a list of procedures for translating
	# possible values to standard ones (as ARG.read would return them)
	# for example tonight in stead of specific UNIX timestamp
	# those procedures return None on failure
	def setValueAliases(self, aliases):
		self.valueAliases = [self.read] + aliases
	
	# possible indicators preceding the value of for this argument
	def setIndicators(self, indicators):
		self.indicators = set(indicators)

	# returns a list of possible values for the argument
	def scanForValues(self, tokens):
		if not self.hasRecognitionData:
			return []
		
		dbg.debug("Scanning for ", self.name)

		ret = []
		ln = len(tokens)
		for i in range(ln):
			if not tokens[i] in self.indicators: continue
			
			for proc in self.valueAliases:
				val = proc(tokens, i+1)
				if not val is None and self.validate(val):
					ret.append(val)
		

		dbg.debug("For", self.name, "found", ret)
		return ret


		

	# creates a read procedure for a list of values with types specified by valTypes
	# returns a list of values on success and None on failure
	@staticmethod
	def makeReader(valTypes):
		def reader(values, start):
			if start + len(valTypes) > len(values):
				return None
			
			ret = []
			for i,valType in enumerate(valTypes):
				if valType=="int": 
					try:
						ret.append(int(values[start+i]))
					except ValueError:
						return None
				if valType=="float": 
					try:
						ret.append(float(values[start+i]))
					except ValueError:
						return None
				if valType=="string": ret.append(str(values[start+i]))
			
			return ret
		
		return reader
	
	# validator that checks whether value is empty
	@staticmethod
	def noVal(value):
		return len(value)==0

	# checks if the list str contains ln words
	@staticmethod
	def isWord(str, ln = 1):
		if len(str) != ln: return False
		for x in str:
			if not x.isalpha(): return False
		return True

	# checks if the list str contains exactly ln integers
	@staticmethod
	def isInt(vals, ln = 1):
		if len(vals) != ln: return False
		for x in vals:
			if type(x)!=int: return False
		return True
			

# class for representing a command
class CMD:

	# creates a simple procedure for validation, which checks
	# whether all the arguments from argList are present in ArgDict
	@staticmethod
	def compulsoryArgs(argList):
		def validator(argDict):
			for arg in argList:
				if not arg in argDict: return False
			return True
		return validator

	def __init__(self, name, arguments, validate, execute, customRecognize = None):

		self.name = name
		self.arguments = arguments		# dictionary with ARG objects by name
		self.validate = validate		# procedure foor checking validity of argument
										# takes a dictionary with entries argname:argval

		self.execute = execute			# procedure for executing a command, takes a Session object as an argument
										# execute procedure takes a Session object and a dictionary with arguments


		self.customRecognize =  customRecognize		# a custom procedure for recognition of this procedure, see recognize

		self.autofill = None			# auto fill the arguments
		self.keywords = set()

	# keywords is a list of keywords by which the command can be recognized
	# self.keywords stores the keywords in a set
	def setKeywords(self, keywords):
		self.keywords = set(keywords)
	
	# set the autofill procedure which takes only one argument
	# the argict and possibly modyfies it by filling in default argument values
	def setAutofill(self, autofill):
		self.autofill = autofill

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
			assert(not vals is None)
			i+=len(vals)


			if argument.validate(vals):
				argumentDict[argument.name] = vals
			
		return argumentDict
	

	# a procedure for recognizing the command from natural language (english)
	# on success returns values of arguments stored in a dictionary,
	# on failure returns None
	# For now operates on limited set of keywords
	def regonize(self, line):
		tokens = re.split(r" |\?|,|\.", line.lower())
		keywordFound = False
		for token in tokens:
			if token in self.keywords: keywordFound = True
		
		dbg.debug(tokens, re.split(line.lower(), " "))
		dbg.debug("Scanned for ", self.name, ", keywords:", keywordFound)

		if not keywordFound: return None

		argDict = dict()

		for argName in self.arguments:
			arg = self.arguments[argName]

			pVals = arg.scanForValues(tokens)
			if len(pVals)==0: continue

			# TODO: change this temporary solution
			argDict[argName] = pVals[0]
		
		if not self.autofill is None:
			self.autofill(argDict)

		if self.validate(argDict): 
			return argDict
		else:
			return None

	
	
