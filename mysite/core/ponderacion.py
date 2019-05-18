import re
import pdb
from unicodedata import normalize

class Evaluador(object):

	def normalizar(self, lista):

		cadena = ' '.join(lista)

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

		suma = 0

		valores = dict_valor

		cadena = cadena.split(' ')

		for c in cadena:
		    if c in valores:
		        suma = suma + valores[c]

		return suma