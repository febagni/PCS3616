import sys
import os.path
from switchcase import *

'''Separate an given string by spaces and remove substrings with 
no content'''
def clean(line):
	res=[]
	line=line.split(" ")
	for word in line:
		if word!="":
			res.append(word)
	return res

#Test if the given file exists, raise error
def valid_file(file):
	if not(os.path.exists(file)):
		raise ValueError("File does not exist")

'''Open given file, read it, clean tabs and separate by enters
(this is the raw descriptor), then remove comments and null lines
(this is the code descriptor), return both descriptors cleaned'''
def load(name):
	valid_file(name)
	file=open(name, "r")
	char=0
	raw=file.read()
	code=""
	raw_mod=""
	#Change tabs to spaces
	while char<len(raw):
		if raw[char]=="\t":
			raw_mod+=" "
		else:
			raw_mod+=raw[char]
		char+=1
	raw_mod=raw_mod.split("\n")
	#The raw file is complete
	code=raw_mod[:]
	line=0
	line_raw=1
	#Cut off all comments, delete empty lines and raise errors 
	while line < len(code):
		try:
			code[line]=code[line][:code[line].index(";")]
		except:
			pass
		code[line]=clean(code[line])
		switch(len(code[line]))
		if case(0):
			code.pop(line)
			line-=1
		#Each line has the line number in the raw code in the end of it
		elif case([2,3]):
			code[line].append(line_raw)
		else:
			raise ValueError("Instrucao mal construida na linha "+str(line_raw))
		line+=1
		line_raw+=1
	#Format raw code
	line=0
	while line<len(raw_mod):
		raw_mod[line]=clean(raw_mod[line])
		line+=1
	return raw_mod, code

#Number format dictionary
num_format={"/":16, 
			"'":"ASCII", 
			"=":10, 
			"@":8, 
			"#":2}

'''Receives an list of two strings as [<type of int>,<int>] and
returns the correspondent integer to the type passed'''
def get_number(num):
	if num_format[num[0]]=="ASCII":
		if len(num[1:])==1:	return ord(num[1:])
		else: return ord(num[1])*0x100+ord(num[2])
	else:
		return int(num[1:], num_format[num[0]])

#Operation dictionary
mnem_op={"K": 0x0,
		"JP":0x0,
		"JZ":0x1, 
		"JN":0x2, 
		"LV":0x3, 
		"AD":0x4, 
		"SB":0x5, 
		"ML":0x6, 
		"DV":0x7, 
		"LD":0x8, 
		"MM":0x9, 
		"SC":0xA, 
		"RS":0xB, 
		"HM":0xC, 
		"GD":0xD, 
		"PD":0xE, 
		"OS":0xF}

file=sys.argv[1]
raw, code=load(file)

#Save entry_points and externals
'''entry_points is a dictionary with entry_points names as indexes 
	and None as values'''
'''externals is a dictionary with externals names as indexes and
	different succesive numbers for each external as values'''
entry_points={}
externals={}
ext_count=0
final=[]
for line in code:
	switch(line[0])
	if case(">"):
		entry_points[line[1]]=None
		final.append(line[1])
	elif case("<"):
		externals[line[1]]=ext_count
		final.append(line[1])
		ext_count+=1

#Define rotules and complete entry_points
rotules={}
rotules_reloc={}
relocable=True
addr=0
for line in code:
	'''len=3 implies format [instru, operand, line_nb]
	where instru can be @, &, $, <, >, operation'''
	'''len=4 implies format [rotule, instu, operand, line_nb]
	where instu can be $, operation'''
	if len(line)==3:
		switch(line[0])
		#Change address relocability
		if case(["@", "&"]):
			relocable=line[0]=="&"
			addr=get_number(line[1])
		#Entry points and externals were already processed
		elif case(">") or case("<"):
			pass
		#Reserve memory
		elif case("$"):
			addr+=2*get_number(line[1])
		#Increment address
		else:
			addr+=2
	elif len(line)==4:
		#Save rotule, it's address and relocability
		rotules[line[0]]=addr
		rotules_reloc[line[0]]=relocable
		#Assign address to entry point
		if line[0] in entry_points:
			entry_points[line[0]]=addr
		switch(line[1])
		#Reserve memory
		if case("$"):
			addr+=2*get_number(line[2])
		#Increment address
		else:
			addr+=2
	else:
		raise ValueError("Instrucao mal formulada na linha "+str(line[-1]))
#Check if all entry points where assigned, raise error
for entry in entry_points:
	if entry_points[entry]==None:
		raise ValueError("Entry point "+entry+" foi indicado, mas não definido")

#Insert entry_points and externals values in final
'''First nibble of the address has the following composition:
[addr relocability][o resolution][op relocability][op location]
  0=abs   1=reloc ||0=res 1=nres||0=abs  1=reloc ||0=in  1=out
Boolean in the last position identify if it is external or entry_point'''
line=0
while line < len(final):
	if final[line] in externals:
		#externals have addr abs, operand n resol, reloc and loc unknown (0)
		final[line]=[0x4000+externals[final[line]], 0x0000, True]
	elif final[line] in entry_points:
		#entry points have addr abs, operand resolved, reloc dependent and in
		final[line]=[rotules_reloc[final[line]]*0x2000+entry_points[final[line]], 0x0000, True]
	line+=1

#Pass through the code defining addresses and translating
addr=0
relocable=True
end=False
line_n=0
for line in code:
	if len(line)==3:
		switch(line[0])
		#symbols for defining relocability
		if case(["@", "&"]):
			relocable=line[0]=="&"
			addr=get_number(line[1])-2
		#symbol for defining constants
		elif case("K"):
			#addr reloc dependent, operand resolved, abs and in
			final.append([8*relocable*0x1000+addr, get_number(line[1]), False])
		#symbol for reserving space
		elif case("$"):
			n=get_number(line[1])
			for i in range(n):
				#addr reloc dependent, operand resolved, abs and in
				final.append([8*relocable*0x1000+addr, 0, False])
				addr+=2
			new_raw=raw[:line_n+2]
			new_raw.extend([[0]]*(n-1))
			new_raw.extend(raw[line_n+2:])
			raw=new_raw
			line_n+=n-1
			addr-=2
		#symbol for ending code
		elif case("#"):
			end=True
			break
		#symbols for instructions
		elif case(mnem_op):
			switch(line[1])
			if case(externals):
				#addr reloc dependent, operand n resolved, abs and out
				final.append([(8*relocable+5)*0x1000+addr, mnem_op[line[0]]*0x1000+externals[line[1]], False])
			elif case(rotules):
				#addr reloc dependent, operand resolved, reloc dependent and in
				final.append([(8*relocable+2*rotules_reloc[line[1]])*0x1000+addr, mnem_op[line[0]]*0x1000+rotules[line[1]], False])
			else:
				#addr reloc dependent, operand resolved, reloc dependent and in
				final.append([10*relocable*0x1000+addr, mnem_op[line[0]]*0x1000+get_number(line[1]), False])
		elif not case("<") and not case(">"):
			raise ValueError("Instrucao mal formulada na linha "+str(line[-1]))
		addr+=2
	elif len(line)==4:
		switch(line[1])
		#symbols for defining relocability
		if case(["@", "&"]):
			relocable=line[1]=="&"
			addr=get_number(line[2])-2
		#symbol for defining constants
		elif case("K"):
			#addr reloc dependent, operand resolved, abs and in
			final.append([8*relocable*0x1000+addr, get_number(line[2]), False])
		#symbol for reserving space
		elif case("$"):
			n=get_number(line[2])
			for i in range(n):
				#addr reloc dependent, operand resolved, abs and in
				final.append([8*relocable*0x1000+addr, 0, False])
				addr+=2
			new_raw=raw[:line_n+2]
			new_raw.extend([[0]]*(n-1))
			new_raw.extend(raw[line_n+2:])
			raw=new_raw
			line_n+=n-1
			addr-=2
		#symbol for ending code
		elif case("#"):
			end=True
			break
		#symbols for instructions
		elif case(mnem_op):
			if line[2] in externals:
				#addr reloc dependent, operand n resolved, abs and out
				final.append([(8*relocable+5)*0x1000+addr, mnem_op[line[1]]*0x1000+externals[line[2]], False])
			elif line[2] in rotules:
				#addr reloc dependent, operand resolved, reloc dependent and in
				final.append([(8*relocable+2*rotules_reloc[line[2]])*0x1000+addr, mnem_op[line[1]]*0x1000+rotules[line[2]], False])
			else:
				#addr reloc dependent, operand resolved, reloc dependent and in
				final.append([10*relocable*0x1000+addr, mnem_op[line[1]]*0x1000+get_number(line[2]), False])
		else:
			raise ValueError("Instrucao mal formulada na linha "+str(line[-1]))
		addr+=2
	line_n+=1

#Check if user ended code
if not end:
	raise ValueError("O código não foi terminado, insira a pseudo-instrução '#' na última linha de seu código")

#Erase line with relocability data from code
line=0
while line < len(code):
	if len(code[line])>1:
		if code[line][0] in ["@", "&"] or code[line][1] in ["@", "&"]:
			code.pop(line)
			line-=1
	line+=1

#Write in output mvn file
mvn_file=open(file[:file.index(".")]+".mvn", "w")
for line in final:
	if line[2]:
		if hex(line[0])[2:].zfill(4)[0]=="4":
			for ext in externals:
				if externals[ext]==int(hex(line[0])[2:].zfill(4)[1:],16): 
					mvn_file.write(hex(line[0])[2:].zfill(4)+" "+hex(line[1])[2:].zfill(4)+" ; '< "+ext+"'\n")
					break
		else:
			for ent in entry_points:
				if entry_points[ent]==int(hex(line[0])[2:].zfill(4)[1:],16): 
					mvn_file.write(hex(line[0])[2:].zfill(4)+" "+hex(line[1])[2:].zfill(4)+" ; '> "+ent+"'\n")
					break
	else:
		mvn_file.write(hex(line[0])[2:].zfill(4)+" "+hex(line[1])[2:].zfill(4)+"\n")
mvn_file.close()

#Write in the output lst file
lst_file=open(file[:file.index(".")]+".lst", "w")
line_code=0
line_final=0
for line in range(len(raw)):
	exit=""
	if len(raw[line])==0:
		pass
	elif raw[line][0]==code[line_code][0] or raw[line][0]==0:
		if code[line_code][0]=="#" or code[line_code][1]=="#":
			break
		exit=hex(final[line_final][0])[2:].zfill(4)+" "+hex(final[line_final][1])[2:].zfill(4)+" ; "
		for word in raw[line]:
			if word!=0: exit+=word+" "
		if word!=0: line_code+=1
		line_final+=1
	else:
		exit+=";"
		for word in raw[line]:
			exit+=word+" "
	lst_file.write(exit+"\n")
lst_file.close()

print("Arquivo "+file+" montado para "+file[:file.index(".")]+".mvn"+" com sucesso!")