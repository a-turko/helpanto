import sys

def printerr(*args):
	print(file=sys.stderr, *args)

def debug(*args):
	print(file=sys.stderr, *args)

def callErr(do_quit,msg):
	printerr(msg)
	if do_quit:
		quit()