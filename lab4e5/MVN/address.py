from mvnutils import *

MIN_VALUE=0x0000
MAX_VALUE=0x00FF
'''
This class is for an address in the memory, it is defined by
one address number and one value contained in this address.
It also contains to get address and value and to set the value
'''
class address:

	#Inicialize address and value
	def __init__(self, addr, value=0x00):
		valid_value(value, MIN_VALUE, MAX_VALUE)
		self.addr=addr
		self.value=value

	def set_value(self, value):
		valid_value(value, MIN_VALUE, MAX_VALUE)
		self.value=value

	def get_addr(self):
		return self.addr

	def get_value(self):
		return self.value

#What a curious man you are, here's another easter egg for you.