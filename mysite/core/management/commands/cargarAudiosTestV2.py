from django.core.management.base import BaseCommand
from mysite.core.models import Audio, Agente, Campaña, Funcion, Palabras, Reporte
import os, time, requests, re
from datetime import datetime, date
from mysite.core.transcriptor import Transcriptor
from mysite.core.ponderacion import Evaluador
from mysite.core.models import Hilo
from bs4 import BeautifulSoup
from unicodedata import normalize
from multiprocessing.dummy import Pool as ThreadPool
import traceback

class Command(BaseCommand):
	args = '<foo bar ...>'
	help = 'our help string comes here'


	def _cargarAudios(self):
		pathTMP = "/home/ubuntu/biometriaTrans/biometria/static/media/audios/tmp/"
		hoy = datetime.today().date()
		_hilo = 0
		ultimo = ""
		if Hilo.objects.filter(hilo=_hilo).exists():
			u = Hilo.objects.get(hilo=_hilo)
			ultimo = u.ultimo
		else:
			u = Hilo.objects.create(hilo=_hilo)
			u.save()
		while hoy == datetime.today().date():
			if os.path.exists("M:/FreeLance/Audios/290910"):
				for r,d,files in os.walk("M:/FreeLance/Audios/290910"):
					
					print ("el ultimo previamente procesado es " + ultimo)
					#Sacamos de la lista de files a los archivos ya procesados del dia
					filesOrdenados = sorted(files, key = lambda str: int(str.split('_')[2]))
					if ultimo == "":
						print ("No habia archivos procesados")
						files_aProcesar = files
						time.sleep(15)
					else:
						#if filesOrdenados[-1] == ultimo
						if filesOrdenados[-1] == ultimo or filesOrdenados[-2] == ultimo or filesOrdenados[-3] == ultimo or filesOrdenados[-4] == ultimo:
							print ("Se proceso el ultimo, esperando 10 minutos")
							time.sleep(15)
							break
						else:
							files_aProcesar = filesOrdenados[filesOrdenados.index(ultimo)+1:]
							print ("Sacando los archivos ya procesados de la lista")
							print ("Se sacaron " + str(filesOrdenados.index(ultimo)) + " archivos de la lista")
							print (files_aProcesar[-4:])
							input()
					
					#Proceso en bloques de a 15 archivos
					for f in files_aProcesar[:15]:
							if f[-3:] == "wav":
								t = Transcriptor()
								e = Evaluador()
								#Para simular hilos usamos modulacion
								if int(f.split("_")[2]) % 4 == _hilo:
									filename = f 
									original = os.path.join(r,f)
									convertir = "ffmpeg  -y -acodec g729 -i " + original + " -acodec pcm_s16le -f wav " + pathTMP + filename
									print (convertir)
									#os.system(convertir)
									if Audio.objects.filter(idInteraccion=("_").join(f.split("_")[2:])[:-4]).exists():
										audio = Audio.objects.get(idInteraccion=("_").join(f.split("_")[2:])[:-4])
									else:
										#audio = Audio.objects.create(inicio=datetime.strptime(f.split("_")[2][0:12], "%y%m%d%H%M%S"), idInteraccion=("_").join(f.split("_")[2:])[:-4],fileOriginal=os.path.join(r,f), file="audios/tmp/"+filename)
										print ("Se crea el audio " + f)
										c1=""
										c2=""
										trans=""
										try:
											#c1, c2, trans = t.parse(audio.file)
											print ("Se transcribe el audio " + f)
										except:
											c1="error"
											c2="error"
											trans="error"
										#ch1 = e.normalizar(c1) 
										#ch2 = e.normalizar(c2)
										#audio.canal_1 = ch1
										#audio.canal_2 = ch2
										#audio.canalOrdenado = trans
										#audio.procesado = False
										#audio.save()
									ultimo = f
									u = Hilo.objects.get(hilo=_hilo)
									u.ultimo = f
									u.save()
									print ("Se seteo como ultimo el " + f)
			else:
				time.sleep(15)

	
	def handle(self, *args, **options):
		self._cargarAudios()
























