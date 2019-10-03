from django.core.management.base import BaseCommand
from mysite.core.models import Audio, Agente, Campaña, Funcion, Palabras, Reporte
import os, time, requests, re, subprocess, logging
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
		_hilo = 2
		logging.basicConfig(filename='/home/ubuntu/cargosAudios'+str(_hilo)+'.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
		ultimo = ""
		if Hilo.objects.filter(hilo=_hilo).exists():
			u = Hilo.objects.get(hilo=_hilo)
			ultimo = u.ultimo
			
			#si quedo cargado con el del dia anterior
			if ultimo.split("_")[2][4:6] != hoy.strftime("%d"):
				ultimo = ""
				u.ultimo = ""
				u.save()
		else:
			u = Hilo.objects.create(hilo=_hilo)
			u.save()
		try:
			while hoy == datetime.today().date():
				if os.path.exists("/mnt/mitrol/"+str(hoy.strftime("%y%m%d"))):
					argument = ["ls", "/mnt/mitrol/"+hoy.strftime("%y%m%d")+"/"]
					proc = subprocess.Popen(argument, stdout=subprocess.PIPE)
					tmp = proc.stdout.read()
					files = tmp.decode("ascii").split("\n")[:-1]
					
					#
					#Sacamos de la lista de files a los archivos ya procesados del dia
					#
					
					
					#ordenamos por la parte de la fecha de creacion
					filesOrdenados_temp = sorted(files, key = lambda str: int(str.split('_')[2]))
					#removemos los ".vnf"
					filesOrdenados = [ x for x in filesOrdenados_temp if ".vnf" not in x ]
					if ultimo == "":
						files_aProcesar = filesOrdenados
					else:
						if filesOrdenados[-1] == ultimo or filesOrdenados[-2] == ultimo or filesOrdenados[-3] == ultimo or filesOrdenados[-4] == ultimo:
							time.sleep(600)
							break
						else:
							files_aProcesar = filesOrdenados[filesOrdenados.index(ultimo)+1:]
					
					#Proceso en bloques de a 20 archivos
					for f in files_aProcesar[:20]:
						t = Transcriptor()
						e = Evaluador()
						#Para simular hilos usamos modulacion
						if filesOrdenados.index(f) % 4 == _hilo:
							filename = f 
							original = os.path.join("/mnt/mitrol/"+hoy.strftime("%y%m%d")+"/",f)
							convertir = "ffmpeg  -y -acodec g729 -i '" + original + "' -acodec pcm_s16le -f wav '" + pathTMP + filename + "' 2> /home/ubuntu/debugInfo"
							logging.info('Path actual '+ os.getcwd())
							logging.info('Conviertiendo audio a pcm_s16e cmd='+convertir)
							os.system(convertir)
							if Audio.objects.filter(idInteraccion=("_").join(f.split("_")[2:])[:-4]).exists():
								audio = Audio.objects.get(idInteraccion=("_").join(f.split("_")[2:])[:-4])
							else:
								audio = Audio.objects.create(inicio=datetime.strptime(f.split("_")[2][0:12], "%y%m%d%H%M%S"), idInteraccion=("_").join(f.split("_")[2:])[:-4],fileOriginal=os.path.join("/mnt/mitrol/"+hoy.strftime("%y%m%d")+"/",f), file="audios/tmp/"+filename)
								c1=""
								c2=""
								trans=""
								#try:
								c1, c2, trans = t.parse(audio.file)
								#except:
								#	c1="error"
								#	c2="error"
								#	trans="error"
								ch1 = e.normalizar(c1) 
								ch2 = e.normalizar(c2)
								audio.canal_1 = ch1
								audio.canal_2 = ch2
								audio.canalOrdenado = trans
								audio.procesado = False
								audio.save()
							ultimo = f
							u = Hilo.objects.get(hilo=_hilo)
							u.ultimo = f
							u.save()
				else:
					time.sleep(600)
		except Exception as e:
			logging.error("Exception occurred", exc_info=True)

	
	def handle(self, *args, **options):
		self._cargarAudios()
























