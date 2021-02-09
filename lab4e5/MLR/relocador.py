import sys
from switchcase import *

def load(name):
	raw=open(name, "r")
	raw=raw.read()
	raw=raw.split("\n")
	code=[]
	for line in raw:
		code.append(line.split(" ")[:-1])
	code.pop(-1)
	return code

#Open all the files
n_params=len(sys.argv)-1
if n_params==0:raise ValueError("Nenhum arquivo fornecido para relocar")
if n_params==1:raise ValueError("Nenhum arquivo de saída definido")
if n_params>3:raise ValueError("Mais parâmetros do que permitido")
name=sys.argv
name.pop(0)
nome=name[1]
base=0
if n_params==3: base=int(name[2], 16)

#Generate code descriptor
file=load(name[0])

#Check if there are any unresolved externals
for line in file:
	if len(line)==5 and line[3]=="'<": raise ValueError("Há externals não resolvidos no código, não pode ser relocado")

#Relocate the entire code
for line in file:
	if len(line)==2:
		addr=int(line[0][1:],16)
		switch(line[0][0])
		if case("a") or case("2"): line[1]=line[1][0]+hex(int(line[1][1:],16)+base)[2:].zfill(3)
		if case("8") and addr+base>0x0fff:raise ValueError("Base incompatível com código")
		line[0]=hex(addr+base)[2:].zfill(4)

#Write to the output file
output=open(nome, "w")
for line in file:
	if len(line)==2:
		for item in line:
			output.write(item+" ")
		output.write("\n")
output.close()

print("Código relocado para "+nome)