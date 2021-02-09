__author__="Miguel Sarraf Ferreira Santucci"
__email__="miguel.sarraf@usp.br"
__version__="1.0"

import MVN
import os.path
from mvnutils import *
from switchcase import *

#Print all the commands available
def help():
	print(" COMANDO  PARÂMETROS           OPERAÇÃO")
	print("---------------------------------------------------------------------------")
	print("    i                          Re-inicializa MVN")
	print("    p     [arq]                Carrega programa para a memória")
	print("    r     [addr] [regs]        Executa programa")
	print("    b                          Ativa/Desativa modo Debug")
	print("    s                          Manipula dispositivos de I/O")
	print("    g                          Lista conteúdo dos registradores")
	print("    m     [ini] [fim]          Lista conteúdo da memória")
	print("    h                          Ajuda")
	print("    x                          Finaliza MVN e terminal")

#Print commands for debugger mode
def dbg_help():
	print(" COMANDO  PARÂMETROS           OPERAÇÃO")
	print("---------------------------------------------------------------------------")
	print("    c                          Continua execução")
	print("    s                          Avança um passo na execução")
	print("    b     [addr]               Insere um breakpoint")
	print("    x                          Pausa execução")
	print("    h                          Ajuda")
	print("    r     [reg] [val]          Atribui valor a registrador")
	print("    a     [addr] [val]         Atribui valor a memória")
	print("    e                          Mostra valores dos registradores")
	print("    m     [ini] [fim]          Lista conteúdo da memória")

'''Start an MVN, check if there is any 'disp.lst' file and 
inicialze the devices in it, return the MVN inicialized'''
def inicialize():
	mvn=MVN.MVN()
	print("MVN Inicializada\n")
	if os.path.exists("disp.lst"):
		mvn.create_disp()
		print("Dispositivos de 'disp.lst' inicializados")
	else:
		print("Inicializacao padrao de dispositivos\n")
	return mvn

#Print the header of the MVN
def head():
	print("                Escola Politécnica da Universidade de São Paulo")
	print("                 PCS3616 - Simulador da Máquina de von Neumann")
	print("          MVN versão 1.0 (Maio/2020) - Todos os direitos reservados")

#Print the header for the devices
def dev_head():
	print("Tipo   UC   Dispositivo")
	print("---------------------------------")

#Print the header for the registers
def reg_head():
	print(" MAR  MDR  IC   IR   OP   OI   AC")
	print("---- ---- ---- ---- ---- ---- ----")

'''Open given file, read it, separate memory and addresses and 
send them to the MVN memory'''
def load(name, mvn):
	valid_file(name)
	file=open(name, "r")
	raw=file.read()
	code=""
	for l in raw:
		if l=="\t":code+=" "
		else:code+=l
	code=code.split("\n")
	line=0
	while line < len(code):
		try:
			code[line]=code[line][:code[line].index(";")]
		except:
			pass
		code[line]=clean(code[line])
		if len(code[line])!=2:
			if len(code[line])==0:
				code.pop(line)
				line-=1
			else:
				raise ValueError("Mais de dois numeros na instrucao")
		line+=1
	mvn.set_memory(code)
	print("Programa "+name+" carregado")

'''Run the code normally using mvn method step. Fisrt thing to do
is define the values of the booleans vals and sbs and then run until
goon turns false'''
def run(mvn, goon, vals, sbs):
	n_steps=0
	if vals:
		s="s"
	else:
		s="n"
	try:
		vals=input("Exibir valores dos registradores a cada passo do ciclo FDE? <s/n> ["+s+"]: ")
		vals=vals=="s" or len(vals)==0
	except:
		vals=True

	if vals:
		if sbs:
			s="s"
		else:
			s="n"
		try:
			sbs=input("Excutar a MVN passo a passo? <s/n> ["+s+"]: ")
			sbs=sbs=="s"
		except:
			sbs=True
	else:
		sbs=False

	if vals:
		reg_head()
		
	while goon:
		goon=mvn.step()
		n_steps+=1
		if vals:
			if sbs:
				read=input(mvn.print_state())
			else:
				print(mvn.print_state())
		if n_steps>max_step:
			print("Limite de passos atingido, verifique se não há loops infinitos.")
			goon=False

'''Run the code in debugger mode, in this mode vals and sbs are not
needed. The debugger mode has it's own instruction set, to execute 
debugging operations, see bdg_help() for complete guide'''
def run_dbg(mvn, goon):
	print("Começando simulação")
	print("Os comandos internos do dbg são")
	dbg_help()
	reg_head()
	step=True
	while goon:
		if step or mvn.IC.get_value() in breakpoints:
			step=False
			out=False
			while not out:
				read=input("(dgb) ").split(" ")
				if not len(read)==0:
					switch(read[0])
					if case("c"):
						out=True
					elif case("s"):
						step=True
						out=True
					elif case("b"):
						if len(read)>1:
							for breaks in read[1:]:
								try:
									breakpoints.append(int(breaks, 16))
								except:
									print("Breakpoint deve ser um valor inteiro hexadecimal")
						else:
							print("Nenhum endereço passado na instrução")
					elif case("x"):
						out=True
						goon=False
					elif case("h"):
						dbg_help()
					elif case("r"):
						if len(read)==3:
							try:
								if read[1] not in ["MAR", "MDR", "IC", "IR", "OP", "OI", "AC"]:
									print("Registrador invalido.")
								elif read[1]=="MAR":
									mvn.MAR.set_value(int(read[2], 16))
								elif read[1]=="MDR":
									mvn.MDR.set_value(int(read[2], 16))
								elif read[1]=="IC":
									mvn.IC.set_value(int(read[2], 16))
								elif read[1]=="IR":
									mvn.IR.set_value(int(read[2], 16))
								elif read[1]=="OP":
									mvn.OP.set_value(int(read[2], 16))
								elif read[1]=="OI":
									mvn.OI.set_value(int(read[2], 16))
								elif read[1]=="AC":
									mvn.AC.set_value(int(read[2], 16))
							except:
								print("Enderecos de memória e valores devem ser inteiros hexadecimais")
					elif case("a"):
						mvn.mem.set_value(int(read[1], 16), int(read[2], 16))
					elif case("e"):
						reg_head()
						print(mvn.print_state())
					elif case("m"):
						mvn.dump_memory(int(read[1], 16), int(read[2], 16))
					else:
						print("Comando não reconhecido\nPressione h para ajuda.")
		goon=mvn.step() and goon
		print(mvn.print_state())


"""
Here starts the main code for the MVN's user interface, this will 
look like a cmd to the user, but operating the MVN class
"""

#Define steps limit
max_step=10000
if os.path.exists("./mvn.config"):
	conf=open("./mvn.config", "r")
	data=conf.read()
	data=data.split("\n")
	line=0
	while line<len(data):
		data[line]=clean(data[line])
		if len(data[line])==0:
			data.pop(line)
			line-=1
		line+=1
	else:
		for line in data:
			text=""
			for word in line:
				text+=word
			if "=" in word:
				switch(word[:word.index("=")])
				if case("max_step"):
					try:
						max_step=int(word[word.index("=")+1:])
					except:
						print("O valor de max_step deve ser inteiro, usando valor padrão.")
				else:
					print("Parâmetro desconhecido, usando valor padrão.")
	conf.close()

#First thing to be done is inicialize our MVN
mvn=inicialize()
#Show up the header for the MVN
head()
#Show options available
help()

'''These booleans will represent if the code should continue to 
execute (goon), if the register values are to be shown on screen 
(vals), if MVN should be executed step by step (sbs) and if the
debugger mode is active (dbg)
'''
goon=False
vals=True
sbs=False
dbg=False

#This loop will deal with the MVN's interface commands
while True:
	command=input("\n> ")
	command=clean(command)

	#No action to be taken if nothing was typed
	if not len(command)==0:
		switch(command[0])
		#To reinicialize the MVN is just to inicialize it one more time
		if case("i"):
			mvn=inicialize()

		#To load an program, one argument (the file) is required, if 
		#it's not given, ask for it, if more are passed, cancel operation
		elif case("p"):
			if len(command)==1:
				name=input("Informe o nome do arquivo de entrada: ")
				name=clean(name)
				if len(name)!=1:
					print("Arquivo deve ter exatamente 1 palavra, "+str(len(command))+" passadas.")
				else:
					load(name[0], mvn)
					goon=True
					pass
			elif len(command)>2:
				print("Arquivo deve ter exatamente 1 palavra, "+str(len(command)-1)+" passadas.")
			else:
				name=command[1]
				load(name, mvn)
				goon=True

		#To run the program we have to ask the user it's preference 
		#on the starting address and call correspondent function to 
		#execute the code dependind if the debugger mode is on
		elif case("r"):
			if goon:
				try:
					mvn.IC.set_value(int(input("Informe o endereco do IC ["+str(hex(mvn.IC.get_value())[2:]).zfill(4)+"]: "), 16))
				except:
					pass
				if not dbg:
					run(mvn, goon, vals, sbs)
				else:
					run_dbg(mvn, goon)
				goon=True	
			else:
				print("Nenhum arquivo foi carregado, nada a ser executado.")

		#Start/stop the debugger mode
		elif case("b"):
			dbg=not dbg
			if dbg:
				print("Modo debugger ativado")
				breakpoints=[]
			else:
				print("Modo debugger desativado")

		#Display the available devices and give options to add or remove
		elif case("s"):
			dev_head()
			mvn.print_devs()
			switch(input("Adicionar(a) ou remover(r) (ENTER para cancelar): "))
			if case("a"):
				mvn.show_available_devs()
				dtype=input("Entrar com o tipo de dispositivo (ou ENTER para cancelar): ")
				try:
					dtype=int(dtype)
					go=True
				except:
					print("O tipo de dispositivo especificado é inválido (especifique um valor numérico).")
					go=False
				if go:
					UC=input("Entrar com a unidade logica (ou ENTER para cancelar): ")
					try:
						UC=int(UC)
						go=True
					except:
						print("O tipo de dispositivo especificado é inválido (especifique um valor numérico).")
						go=False
				if go:
					if dtype==2:
						name=input("Entrar com o nome da impressora: ")
						mvn.new_dev(dtype, UC, printer=name)
					elif dtype==3:
						file=input("Digite o nome do arquivo: ")
						met=input("Digite o modo de operação -> Leitura(l), Escrita(e) ou Leitura e Escrita(b): ")
						mvn.new_dev(dtype, UC, file, met)
					else:
						mvn.new_dev(dtype, UC)
					print("Dispositivo adicionado (Tipo: "+str(dtype)+" - unidade logica: "+str(UC)+")")
			elif case("r"):
				mvn.show_available_devs()
				dtype=input("Entrar com o tipo de dispositivo (ou ENTER para cancelar): ")
				try:
					dtype=int(dtype)
					go=True
				except:
					print("O tipo de dispositivo especificado é inválido (especifique um valor numérico).")
					go=False
				if go:
					UC=input("Entrar com a unidade logica (ou ENTER para cancelar): ")
					try:
						UC=int(UC)
						go=True
					except:
						print("O tipo de dispositivo especificado é inválido (especifique um valor numérico).")
						go=False
				if go:
					mvn.rm_dev(dtype, UC)

		#Display actual state os the MVN registers
		elif case("g"):
			reg_head()
			print(mvn.print_state())

		#Display the memmory of the MVN given the start and end addresses
		elif case("m"):
			if len(command)==3:
				try:
					start=int(command[1], 16)
					stop=int(command[2], 16)
					mvn.dump_memory(start, stop)
				except:
					print("Enderecos não são valores hexadecimais.")
			elif len(command)==4:
				try:
					start=int(command[1], 16)
					stop=int(command[2], 16)
					mvn.dump_memory(start, stop, command[3])
				except:
					print("Enderecos não são valores hexadecimais.")
			elif len(command)>4:
				print("Mais valores passados que parâmetros.")
			else:
				try:
					start=int(input("Informe o endereco inicial: "), 16)
					stop=int(input("Informe o endereco final: "), 16)
					mvn.dump_memory(start, stop)
				except:
					print("Enderecos não são valores hexadecimais.")

		#Display the available commands
		elif case("h"):
			help()
			
		#Exit terminal
		elif case("x"):
			for dev in mvn.devs:
				dev.terminate()
			print("Terminal encerrado.")
			exit()