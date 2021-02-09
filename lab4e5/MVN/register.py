from mvnutils import *

MIN_VALUE=0x0000
MAX_VALUE=0xFFFF

'''
This class is for an register in the MVN, it has only it's
own value.
It also has methods to get and set this value
'''
class register:

	#Inicialize the register with value
	def __init__(self, value=0x00):
		valid_value(value, MIN_VALUE, MAX_VALUE)
		self.value=value

	def set_value(self, value):
		valid_value(value, MIN_VALUE, MAX_VALUE)
		self.value=value
		
	def get_value(self):
		return self.value