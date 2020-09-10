
# This module implements the lingvoy command for handling translations

import requests
from bs4 import element as bs4element
from bs4 import BeautifulSoup
import debugtools as dbg

class Languages:
	shortName = { "english":"EN", "german":"DE", "spanish":"ES", "polish":"PL", "french":"FR", \
		"italian":"IT", "swedish":"SV"}
	longName = { "EN":"english", "DE":"german", "ES":"spanish", "PL":"polish", "FR":"french",\
		"IT":"italian", "SV":"swedish"}

	dataType = {"noun": "wordType", "verb":"wordType", "adjective":"wordType", "adverb":"wordType", \
		"preposition":"wordType", \
		"masculine":"gender", "feminine":"gender"}
	
	# packs the information into the dictionary
	@classmethod
	def grammar(cls, info):
		ret = dict()
		for w in info:
			w = w.rstrip(" ,;:*")
			if w in cls.dataType:
				ret[cls.dataType[w]] = w
		return ret

	# checks whether s is a statement
	# TODO: implement somthing better
	@classmethod
	def properStatement(cls, s):
		return len(s)>6

# Bautiful Soup helper
class BSH:
	@staticmethod
	def hasAttr(tag, name, value):
		if name not in tag.attrs:
			return False
		return tag[name]==value
		

class Translation:
	def __init__(self, word, language = None, grammar = dict(), examples = []):
		self.word = word
		self.language = language
		self.grammar = grammar
		# list of pairs [example, its translation]
		self.examples = examples
		return

	def debug(self, more = False):
		dbg.debug("    ", self.word, "(", self.language, ")", self.grammar)
		if more:
			for example in self.examples:
				dbg.debug("        ", example)

class Word:
	def __init__(self, word, language = None, wordType = None, translations = [], grammar = dict()):
		self.word = word
		self.language = language
		self.wordType = wordType
		self.translations = translations
		self.grammar = grammar
	
	#decide whether these classes represent the same word
	@staticmethod
	def matching(word1, word2):
		def check(x, y):
			return x is None or y is None or x==y
		
		return check(word1.word, word2.word) and check(word1.language, word2.language) \
			and check(word1.wordType, word2.wordType)

	def debug(self, lvl = 0):
		if lvl==0:
			dbg.debug("\nPrinting word ", self.word, " in ", self.language)
		else:
			dbg.debug("\nPrinting word ", self.word, "(", self.wordType, ")", " in ", self.language,\
				": ", self.grammar)
		dbg.debug("Translations: ")
		if lvl>0:
			for t in self.translations:
				t.debug((lvl>1))


class Linguee:
	Site = "https://www.linguee.com/"
	def get_url(self, lang1, lang2,word):
		return "{}{}-{}//search?source=auto&query={}".format(self.Site, lang1, lang2, word)   



	# get a translation
	def translation(self, translationEntry, lang1 = None, lang2 = None):
		
		# Collect translation
		header = translationEntry.find(class_ = "translation_desc")
		if header is None:
			dbg.printerr("Failed to find translation description")
			return None
		
		wordInfo = header.find(href = True)
		if wordInfo is None:
			dbg.printerr("Failed to find the translated word (WordInfo)")
			return None
		
		word = None
		for w in wordInfo.children:
			if type(w)==bs4element.NavigableString and (word is None or len(word) < len(str(w))):
				word = str(w)
		

		if word is None:
			dbg.printerr("Failed to read the translated word(word)")
			dbg.printerr(wordInfo.prettify())
			return None
		

		
		grammarInfo = header.find(title = True)
		grammar = dict()

		if not grammarInfo is None:
			info = grammarInfo['title'].split()
			grammar = Languages.grammar(info)

		# Collect examples
		examples = []
		exampleLines = translationEntry.find(class_ = "example_lines")
		if not exampleLines is None:
			for exampleInfo in exampleLines.find(class_ = "example line"):
				example = []
				for s in exampleInfo.stripped_strings:
					s = str(s)
					if Languages.properStatement(s):
						example.append(s)
				
				examples.append(tuple(example))
		
		Trans = Translation(word, lang2, grammar, examples)

		return Trans
	
	def getWord(self, dictEntry, lang1 = None, lang2 = None):
		
		# Collect information about the word

		header = dictEntry.find(class_ = "line lemma_desc")

		if header is None:
			dbg.printerr("Failed to collect information about the word")
			return None

		strings = [s for s in header.stripped_strings]
		if len(strings)<2:
			dbg.printerr("Gathered too little information about the word")
			return None
		
		word = strings[0]
		wordType = ""

		# identifying a word type
		for s in strings[1:]:
			if len(wordType)==0: wordType = s
			elif (not wordType in Languages.dataType or Languages.dataType[wordType]!="wordType"):
				if s in Languages.dataType and Languages.dataType[s]=="wordType":
					wordType = s
		


		# Collect translations

		Trans = []
		translations = dictEntry.find(class_ = "translation_lines")

		if translations is None:
			dbg.printerr("No translations found!")
			return None
		
		for t in translations.children:
			
			if isinstance(t, str):
				continue

			if not "class" in t.attrs:
				continue

			c = t['class']

			if len(c)<2 or c[0]!="translation" or c[1]!="sortablemg":
				continue
			
			tr = self.translation(t, lang1, lang2)
			if tr is None:
				continue
			
			Trans.append(tr)

		
		# Create and return the Word class

		ret = Word(word,lang1, wordType, Trans)

		return ret


	#returns a list of possible words with translations
	def query(self, lang1, lang2, word):
		# Get the site

		url = self.get_url(lang1, lang2, word)
		print(url)

		try:
			response = requests.get(url, timeout=5)
		except requests.exceptions.Timeout:
			dbg.printerr("The connection has timed out")
		
		site_soup = BeautifulSoup(response.content, "html.parser")
		

		# DEBUG
		site = open("site.html", 'w')

		print(site_soup.prettify(), file = site)
		site.close()
		# END OF DEBUG

		# Search the dictionary

		d_tag = site_soup.find(id = "dictionary")

		#dbg.debug(d_tag.prettify())

		if d_tag is None:
			dbg.printerr("Didn't find the result from dictionary")
			return None

		dictPage = None
		for tag in (d_tag.find_all(class_ = "isMainTerm") + d_tag.find_all(class_ = "isForeignTerm")):
			
			#dbg.debug("Found a main term")
			#dbg.debug(tag.prettify())

			if not BSH.hasAttr(tag, "data-source-lang", Languages.shortName[lang1]):
				continue
			# Found the right tag
			dictPage = tag

		if dictPage is None:
			# Din't find the right page
			dbg.printerr("Didn't find the right page")
			return None

		results = []
		for entry in dictPage.find_all(class_ = "lemma featured"):
			result = self.getWord(entry, lang1, lang2)
			if result is None:
				continue

			results.append(result)
		

		return results


# definition of the lingvoy command
from commands import ARG
from commands import CMD

# definitions of arguments (mandatory arguments  are preceeded by *)

ArgDict = dict()

# checks whether str is a valid language name (valid language names are two-letter codes: EN, DE, ES etc.)
def isLanguageCode(str):
	return len(str)==1 and str[0] in Languages.longName


# *SourceLang
ArgDict["slang"] = ARG("slang", isLanguageCode, ARG.makeReader(["string"]))
# *DestLang
ArgDict["dlang"] = ARG("dlang", isLanguageCode, ARG.makeReader(["string"]))
# *Word
ArgDict["word"] = ARG("word", ARG.isWord, ARG.makeReader(["string"]))
# Example -- list examples
ArgDict["example"] = ARG("example", ARG.noVal, ARG.makeReader([]))
# Translation -- show translations
ArgDict["trans"] = ARG("trans", ARG.noVal, ARG.makeReader([]))
# Grammar -- present grammarInfo
ArgDict["grammar"] = ARG("grammar", ARG.noVal, ARG.makeReader([]))
# Languages -- print information about the languages 
ArgDict["lang"] = ARG("lang", ARG.noVal, ARG.makeReader([]))
# Print all the information
ArgDict["all"] = ARG("all", ARG.noVal, ARG.makeReader([]))


# data for command recognition

# tries to recognize a language code
def langCode(tokens, start):
	if start >= len(tokens):
		return None
	
	if tokens[start] in Languages.shortName:
		return Languages.shortName[tokens[start]]
	
	code = tokens[start].upper()

	if code in Languages.longName:
		return code
	
	return None

ArgDict["slang"].setIndicators(["from", "in"])
ArgDict["slang"].setValueAliases([langCode])
ArgDict["slang"].hasRecognitionData = True

ArgDict["dlang"].setIndicators(["to"])
ArgDict["dlang"].setValueAliases([langCode])
ArgDict["dlang"].hasRecognitionData = True

ArgDict["word"].setIndicators(["translate", "word"])
ArgDict["word"].setValueAliases([])
ArgDict["word"].hasRecognitionData = True

ArgDict["example"].setIndicators(["example", "usage", "sentence", "context"])
ArgDict["example"].setValueAliases([])
ArgDict["example"].hasRecognitionData = True

ArgDict["trans"].setIndicators(["translate", "translation", "mean", "meaning"])
ArgDict["trans"].setValueAliases([])
ArgDict["trans"].hasRecognitionData = True

ArgDict["grammar"].setIndicators(["grammar"])
ArgDict["grammar"].setValueAliases([])
ArgDict["grammar"].hasRecognitionData = True

def autofill(argDict):
	if not "dlang" in argDict:
		argDict["dlang"] = "EN"
	if not "slang" in argDict:
		argDict["slang"] = "EN"

# definition of the command
# TODO: test the command interface
def execute(session, arguments):

	dbg.debug("Executing lingvoy with args: ", arguments)

	if "all" in arguments:
		for name in ArgDict:
			if ArgDict[name].validate is ARG.noVal and not name in arguments:
				arguments[name] = []

	if session.languages is None:
		dbg.debug("Setting a new dictionary")
		session.languages = Linguee()
	
	slang = arguments["slang"][0]
	source = Languages.longName[slang]
	dlang = arguments["dlang"][0]
	dest = Languages.longName[dlang]
	word = arguments["word"][0]
	resultList = session.languages.query(source, dest, word)

	for result in resultList:
		print(result.word, end = '')
		if "lang" in arguments: 
			print(" ({})".format(result.language), end = '')

		if not result.wordType is None: 
			print(" ({})".format(result.wordType), end = '')
		

		# print grammar info about the word
		if "grammar" in arguments: 
			first = True
			for info in result.grammar:
				if not first: print(',')
				print(" {}: {}".format(info, result.grammar[info]), end = '')
				first = False

		print()
		
		# print the translations:

		for translation in result.translations:

			if "trans" in arguments:
				print("  " + translation.word, end = '')

				if "lang" in arguments:
					print(" ({})".format(translation.language), end = '')
				
				if "grammar" in arguments and len(translation.grammar) > 0:
					print(" (", end = '')
					first = True
					for info in translation.grammar:
						if not first: print (", ", end = '')
						first = False
						print("{}: {}".format(info, translation.grammar[info]), end= '')
					print(")", end = '')
				
				print()
			
			if "example" in arguments:
				for example in translation.examples:
					print("    " + example[0])

					if "trans" in arguments:
						print("    " + example[1])
		

	# finished execution with success
	return True


Lingvoy = CMD("lingvoy", ArgDict, CMD.compulsoryArgs(["word", "slang", "dlang"]), execute, customRecognize = None)
Lingvoy.setKeywords(["translate", "translation", "mean", "means", "meaning", "useage", "sentence", "context", "grammar"])
Lingvoy.setAutofill(autofill)


# for testing

if __name__ == "__main__":


	LG = Linguee()

	word, lang1, lang2 = input().split()

	result = LG.query(lang1, lang2, word)

	for word in result:
		word.debug(2)
