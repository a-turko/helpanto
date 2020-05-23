import sys

def printerr(*args):
	print(file=sys.stderr, *args)

def debug(*args):
	print(file=sys.stderr, *args)