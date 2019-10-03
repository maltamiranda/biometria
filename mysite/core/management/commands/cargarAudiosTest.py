from django.core.management.base import BaseCommand
from mysite.core.models import Audio, Agente, Campaña, Funcion, Palabras, Reporte
import os, time, requests, re
from datetime import datetime, date
from mysite.core.transcriptor import Transcriptor
from mysite.core.ponderacion import Evaluador
from bs4 import BeautifulSoup
from unicodedata import normalize
from multiprocessing.dummy import Pool as ThreadPool
import traceback

class Command(BaseCommand):
	args = '<foo bar ...>'
	help = 'our help string comes here'

	def _cargarReportes(self, a):
		try:
			for f in funciones:
				e = Evaluador()
				suma = e.ponderizar(a.canal_1.lower(), Palabras.objects.filter(fk_funcion=f))
				canalOrdenado_resaltado = a.canalOrdenado
				canalOrdenado_resaltadoFinal = ""
				canalOrdenado_resaltado = canalOrdenado_resaltado.split("||")[:-1]
				for bloque in canalOrdenado_resaltado:
					b = bloque.split("|")
					if b[1] == "operador":
						bloqueTrans = b[2]
						bloqueTrans = bloqueTrans.lower()
						# -> NFD y eliminar diacríticos
						bloqueTrans = re.sub(
								r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
								normalize( "NFD", bloqueTrans), 0, re.I
							)
						# -> NFC
						bloqueTrans = normalize( 'NFC', bloqueTrans).split(" ")
						for palabra in Palabras.objects.filter(fk_funcion=f):
							#if palabra.palabra.lower() in bloqueTrans:
							for indice,palabra_Canal_1 in enumerate(bloqueTrans):
								if palabra.palabra.lower() == palabra_Canal_1:
									bloqueTrans[indice] = palabra_Canal_1.replace(palabra.palabra.lower(),'<b>'+palabra.palabra.lower()+'</b>')
						bloqueTrans = " ".join(bloqueTrans)
						canalOrdenado_resaltadoFinal = canalOrdenado_resaltadoFinal + b[0] + "|" + b[1] + "|" + bloqueTrans + "||"
					else:
						canalOrdenado_resaltadoFinal = canalOrdenado_resaltadoFinal + bloque + "||"
				
				
				
				#for palabra in Palabras.objects.filter(fk_funcion=f):
				#	if palabra.palabra.lower() in canal_1_resaltado:
				#		for indice,palabra_Canal_1 in enumerate(canal_1_resaltado):
				#			if palabra.palabra.lower() == palabra_Canal_1:
				#				canal_1_resaltado[indice] = palabra_Canal_1.replace(palabra.palabra.lower(),'<b>'+palabra.palabra.lower()+'</b>')
				#canal_1_resaltado = " ".join(canal_1_resaltado)
				#analisis = random.randint(0, 100)
				Reporte.objects.create(ponderacion=suma, 
									fk_audio=a,
									fk_funcion=f,
									#canal_1=canal_1_resaltado,
									#canal_2=a.canal_2,
									canalOrdenado = canalOrdenado_resaltadoFinal[:-2],
									nombre_agente = a.agente.nombre,
									nombre_audio = a.idInteraccion,
									nombre_campaña = a.campaña.nombre,
									fecha_audio = a.inicio)
		except:
			pass

		
	def _cargarAudios(self):
		pathTMP = "/home/ubuntu/biometriaTrans/biometria/static/media/audios/tmp/"
		hoy = datetime.today().date()
		ultimo = ""
		while hoy == datetime.today().date():
			if os.path.exists("/mnt/mitrol/"+str(hoy.strftime("%y%m%d"))):
				for r,d,files in os.walk("/mnt/mitrol/"+str(hoy.strftime("%y%m%d"))):
					filesOrdenados = sorted(files, key = lambda str: int(str.split('_')[2]))
					if ultimo == "":
						files_aProcesar = files
					else:
						if filesOrdenados[-1] == ultimo:
							time.sleep(600)
							break
						else:
							files_aProcesar = filesOrdenados[filesOrdenados.index(ultimo)+1:]
					for f in files_aProcesar[:50]:
						#try:
							if f[-3:] == "wav":
								t = Transcriptor()
								e = Evaluador()
								if True:#int(f.split("_")[2]) % 4 == 0:
									filename = f 
									original = os.path.join(r,f)
									convertir = "ffmpeg  -y -acodec g729 -i " + original + " -acodec pcm_s16le -f wav " + pathTMP + filename
									os.system(convertir)
									if Audio.objects.filter(idInteraccion=("_").join(f.split("_")[2:])[:-4]).exists():
										audio = Audio.objects.get(idInteraccion=("_").join(f.split("_")[2:])[:-4])
									else:
										audio = Audio.objects.create(inicio=datetime.strptime(f.split("_")[2][0:12], "%y%m%d%H%M%S"), idInteraccion=("_").join(f.split("_")[2:])[:-4],fileOriginal=os.path.join(r,f), file="audios/tmp/"+filename)
										c1=""
										c2=""
										trans=""
										#try:
										c1, c2, trans = t.parse(audio.file)
										#except:
										#	pass
										ch1 = e.normalizar(c1) 
										ch2 = e.normalizar(c2)
										audio.canal_1 = ch1
										audio.canal_2 = ch2
										audio.canalOrdenado = trans
										audio.procesado = False
										audio.save()
							ultimo = f
						#except:
						#	pass
					break
				break
			else:
				time.sleep(600)
			break

		
	def _cargarPonderacionAudio(self,a):
		try:			
			pond = 0.00
			cant = 0
			for r in Reporte.objects.filter(fk_audio=a):
				pond = pond + r.ponderacion
				cant += 1
			a.ponderacion = pond/cant
			a.save()
		except:
			pass
	
	def handle(self, *args, **options):
		self._cargarAudios()
