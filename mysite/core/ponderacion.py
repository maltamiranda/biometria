import re
import pdb
from unicodedata import normalize

class Evaluador(object):

	def normalizar(self, lista):

		cadena = '|'.join(lista)

		cadena = cadena.lower()

		# -> NFD y eliminar diacríticos
		cadena = re.sub(
		        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
		        normalize( "NFD", cadena), 0, re.I
		    )

		# -> NFC
		cadena = normalize( 'NFC', cadena)

		return cadena

	def calificar(self, cadena, dict_valor, frase):
		
		cadena = cadena.replace("|"," ")
		suma = 0
		cadena = cadena.split(' ')
		
		temp_frase = []
		
		for p in frase:
			if "/" in p:
				temp = []
				for t in p.split("/"):
					temp.append(t)
				temp_frase.append(temp)
			elif "@" in p:
				temp_frase.append(True)
			else:
				temp_frase.append(p)

		for c in cadena:
			if c in dict_valor:
				suma = suma + dict_valor[c]
				del dict_valor[c]

		return suma
		
	def ponderizar(self, canal1, palabras):
	
		cadena = canal1.replace("|"," ")
		suma = 0
		canal1_temp = set(canal1.split(" "))
		for p in palabras:
			for pCanal in canal1_temp:
				if p.palabra.lower() == pCanal:
					suma = suma + p.porcentaje
		
		return suma