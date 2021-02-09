value=[None]
def switch(var):
	value[0]=var

def case(var):
	if type(var)==list or type(var)==dict:
		return value[0] in var
	return value[0]==var