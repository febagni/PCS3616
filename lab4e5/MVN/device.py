import subprocess
from mvnutils import *
from switchcase import *

MIN_VALUE=0x0000
MAX_VALUE=0xFFFF

'''
This class represents an simple I/O device for MVN, it can
hold monitor (output), keyboard (input), printer (output) 
or file (input and/or output).
It contains methods to return weather the device is readable
or writable, to input and output data, to get device type and 
UC, to print the possible devices and to terminate it.
'''
class device:

	'''Inicialize the device given the type, the UC and other
	convinient parameters'''
	def __init__(self, dtype, UC, file=None, rwb=None, printer=None):
		valid_type(dtype)
		self.dtype=dtype
		self.UC=UC
		if self.dtype==3:
			valid_rwb(rwb)
			switch(rwb)
			if case("e"):
				self.file_write=open(file, "wb")
				self.file_read=None
			elif case("l"):
				valid_file(file)
				self.file_write=None
				self.file_read=open(file, "rb")
				self.buffer=self.file_read.read()
				self.counter=0
			elif case("b"):
				valid_file(file)
				self.file_write=open(file, "wb")
				self.file_read=open(file, "ab")
				self.buffer=self.file_read.read()
				self.counter=0
				self.file_write.write(bytes(self.buffer, "UTF-8"))
		elif self.dtype==2:
			valid_printer(printer)
			self.printer=printer
		elif self.dtype==0:
			self.buffer=[]

	#Return True weather the device is readable
	def is_readable(self):
		return self.dtype==0 or (self.dtype==3 and self.file_read!=None)

	#Return True weather the device is writable
	def is_writable(self):
		return self.dtype==1 or self.dtype==2 or self.dtype==3 and self.file_write!=None

	'''
	             .-.
	       ..==./xxx\
	      /<<<<<\    |
	      \>>>>>/xxxx/--.
	       `'==''---; * *`\
	                \* * */
	                 '--'`
	'''

	'''Get data from the device and return it, the limit to be 
	returned is one byte (or two nibbles)'''
	def get_data(self):
		if not self.is_readable():
			raise MVNError("Unreadable device")
		switch(self.dtype)
		if case(0):
			if len(self.buffer)<2:
				read=input()
				for nibble in read:
					self.buffer.append(ord(nibble))
				self.buffer.append(ord("\n"))
			return self.buffer.pop(0)*0x0100+self.buffer.pop(0)
		elif case(3):
			if self.counter+2>len(self.buffer):
				print("No more data to get, returning 0x0000")
				return 0x0000
			else:
				self.counter+=2
				return self.buffer[self.counter-2]*0x0100+self.buffer[self.counter-1]

	'''Put given data to the device, the limit to be put is one
	byte (or two nibbles)'''
	def put_data(self, value):
		if not self.is_writable():
			raise MVNError("Unwritable device")
		valid_value(value, MIN_VALUE, MAX_VALUE)
		switch(self.dtype)
		if case(1):
			print(chr(value//0x0100)+chr(value%0x0100))
		elif case(2):
			out=open("will_print.txt", "rb")
			out.write(value//0x0100)
			out.write(value%0x0100)
			subprocess.run("lpr -P "+self.printer+" will_print.txt")
			subprocess.run("rm will_print.txt")
		elif case(3):
			self.file_write.write((value//0x0100).to_bytes(1,byteorder="big"))
			self.file_write.write((value%0x0100).to_bytes(1,byteorder="big"))

	#Ends up the device
	def terminate(self):
		if self.dtype==3:
			try:
				self.file_write.close()
			except:
				pass

			try:
				self.file_read.close()
			except:
				pass

	#Return device type
	def get_type(self):
		return self.dtype

	#Return device UC
	def get_UC(self):
		return self.UC

	#Print the possible devices
	def show_available(self):
		print("Tipos de dispositivos disponíveis:")
		print("   Teclado    -> 0")
		print("   Monitor    -> 1")
		print("   Impressora -> 2")
		print("   Disco      -> 3")



#Easter eggs taken from https://www.oocities.org/spunk1111/easter.htm