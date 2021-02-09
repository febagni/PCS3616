import os.path
import subprocess

#Error class
class MVNError(Exception):
	pass

#Test if argument is between MIN and MAX, raise error
def valid_value(num, MIN, MAX):
	if not(MIN<=num and num<=MAX):
		raise MVNError("Incompatible size")

#Test if argument is 1,2,4,5,6 or 7, raise error
def valid_instru(num):
	if num not in [1,2,4,5,6,7]:
		raise MVNError("Incompatible instruction")

#Test if argument is between 0 and 4, raise error
def valid_type(val):
	if not(val>=0 and val<=3):
		raise MVNError("Incompatible type")

#Test if the given file exists, raise error
def valid_file(file):
	if not(os.path.exists(file)):
		raise MVNError("File does not exist")

#Test if given rwb is valid, raise error
def valid_rwb(rwb):
	if rwb not in ["e", "l", "b"]:
		raise MVNError("Incompatible parameter")

#Test if the printer exists in OS, raise error
def valid_printer(printer):
	try:
		out=subprocess.check_output(["lpstat", "-p", printer])
	except:
		raise MVNError("Impressora invalida")

'''Separate an given string by spaces and remove substrings with 
no content'''
def clean(line):
	res=[]
	line=line.split(" ")
	for word in line:
		if word!="":
			res.append(word)
	return res

#Really? You had to check this methods???