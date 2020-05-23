
# lingvoj -- a language helper module:
# handles searching for translations, example usage and such

import requests
from bs4 import BeautifulSoup
import debugtools as dbg
import re

class Languages:
	shortName = { "english":"EN", "german":"DE", "spanish":"ES", "polish":"PL"}
	longName = { "EN":"english", "DE":"german", "ES":"spanish", "PL":"polish"}

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
		# list of pairs [example, its translations]
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
			dbg.printerr("Failed to find the translated word")
			return None
		
		word = wordInfo.string
		if word is None:
			dbg.printerr("Failed to read the translated word")
			return None
		
		word = str(word)
		
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
		wordType = strings[1]

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

		if d_tag is None:
			dbg.printerr("Didn't find the result from dictionary")
			return None

		dictPage = None
		for tag in d_tag.find_all(class_ = "isMainTerm"):
			if not BSH.hasAttr(tag, "data-source-lang", Languages.shortName[lang1]):
				continue
			# Found the right tag
			dictPage = tag

		if dictPage is None:
			# Din't find the right page
			return None

		results = []
		for entry in dictPage.find_all(class_ = "lemma featured"):
			result = self.getWord(entry, lang1, lang2)
			if result is None:
				continue

			results.append(result)
		

		return results



# for testing

if __name__ == "__main__":

	LG = Linguee()

	word, lang1, lang2 = input().split()

	result = LG.query(lang1, lang2, word)

	for word in result:
		word.debug(2)
