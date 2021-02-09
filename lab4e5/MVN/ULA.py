from mvnutils import *
from switchcase import *

MIN_VALUE=0x0000
MAX_VALUE=0xFFFF

'''
This class represents an simple Logic and Arthimatic Unit 
(LAU), here called by ULA (in portuguese), this LAU can only
operate equal zero, less than zero, addition, subtraction, 
multiplication and division mapped in the operations 1,2,4,5,6,7
respectively.
It contains methods for all of these operations and one method 
to call the others.
'''
class ULA:
	#Inicialize the LAU
	def __init__(self):
		pass

	'''Check if the given instruction is valid and performs the
	right operation'''
	def execute(self, op, ac, oi=0x0000):
		valid_instru(op)
		valid_value(ac, MIN_VALUE, MAX_VALUE)
		valid_value(oi, MIN_VALUE, MAX_VALUE)
		switch(op)
		if case(1):
			return self.is_zero(ac)
		elif case(2):
			return self.is_neg(ac)
		elif case(4):
			return self.add(ac, oi)
		elif case(5):
			return self.sub(ac, oi)
		elif case(6):
			return self.mul(ac, oi)
		elif case(7):
			return self.div(ac, oi)
	
	def is_zero(self, num):
		return num==0x0000

	def is_neg(self, num):
		return num>=0x8000

	def add(self, num1, num2):
		return (num1+num2)%(1<<16)

	def sub(self, num1, num2):
		return (num1-num2)%(1<<16)

	def mul(self, num1, num2):
		return (num1*num2)%(1<<16)

	def div(self, num1, num2):
		signal=False
		if self.is_neg(num1):
			num1=self.mul(num1, 0xFFFF)
			signal=not signal
		if self.is_neg(num2):
			num2=self.mul(num2, 0xFFFF)
			signal=not signal
		if signal:
			return self.mul(num1//num2, 0xFFFF)
		return num1//num2