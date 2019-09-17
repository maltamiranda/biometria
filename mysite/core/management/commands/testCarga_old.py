from django.core.management.base import BaseCommand
from mysite.core.models import Audio, Agente, Campaña, Funcion, Palabras, Reporte
import os, time, requests
from datetime import datetime, date
from mysite.core.transcriptor import Transcriptor
from mysite.core.ponderacion import Evaluador
from bs4 import BeautifulSoup

class Command(BaseCommand):
	args = '<foo bar ...>'
	help = 'our help string comes here'

	def _cargarReportes(self):
		audios = Audio.objects.all()
		for a in audios:
			funciones = a.campaña.fk_funciones.all()
			for f in funciones:
				e = Evaluador()
				suma = e.ponderizar(a.canal_1.lower(), Palabras.objects.filter(fk_funcion=f))
				canal_1_resaltado= a.canal_1
				canal_1_resaltado = canal_1_resaltado.split(" ")
				for palabra in Palabras.objects.filter(fk_funcion=f):
					if palabra.palabra.lower() in canal_1_resaltado:
						for indice,palabra_Canal_1 in enumerate(canal_1_resaltado):
							if palabra.palabra.lower() == palabra_Canal_1:
								canal_1_resaltado[indice] = palabra_Canal_1.replace(palabra.palabra.lower(),'<b>'+palabra.palabra.lower()+'</b>')
				canal_1_resaltado = " ".join(canal_1_resaltado)
				#analisis = random.randint(0, 100)
				Reporte.objects.create(ponderacion=suma, 
									fk_audio=a,
									fk_funcion=f,
									canal_1=canal_1_resaltado,
									canal_2=a.canal_2,
									nombre_agente = a.agente.nombre,
									nombre_audio = a.idInteraccion,
									nombre_campaña = a.campaña.nombre,
									fecha_audio = a.inicio)


	def _cargarTranscripciones(self):
		for audio in Audio.objects.all():
			t = Transcriptor()
			e = Evaluador()
			c1, c2 = t.parse(audio.file)
			ch1 = e.normalizar(c1) 
			ch2 = e.normalizar(c2)
			audio.canal_1 = ch1
			audio.canal_2 = ch2
			audio.save()
	
	def _cargarAudios(self):
		stats = open("stats.csv","w")
		pathTMP = "static/media/audios/tmp/"
		t = Transcriptor()
		e = Evaluador()
		for r,d,files in os.walk("/mnt/mitrol/"+str(date.today().strftime("%y%m%d"))):
			for f in files:
				filename = f 
				original = os.path.join(r,f)
				start_time = time.time()
				convertir = "ffmpeg   -acodec g729 -i " + original + " -acodec pcm_s16le -f wav " + pathTMP + filename
				os.system(convertir)
				if Audio.objects.filter(idInteraccion=("_").join(f.split("_")[2:])[:-4]).exists():
					audio = Audio.objects.get(idInteraccion=("_").join(f.split("_")[2:])[:-4])
				else:
					audio = Audio.objects.create(inicio=datetime.strptime(f.split("_")[2][0:12], "%y%m%d%H%M%S"), idInteraccion=("_").join(f.split("_")[2:])[:-4],fileOriginal=os.path.join(r,f), file="audios/tmp/"+filename)
				c1, c2 = t.parse(audio.file)
				ch1 = e.normalizar(c1) 
				ch2 = e.normalizar(c2)
				audio.canal_1 = ch1
				audio.canal_2 = ch2
				audio.save()
				elapsed_time = time.time() - start_time
				stats.write(str(start_time)+"|"+str(elapsed_time)+"\n")
		stats.close()
		
	def _cargarPonderacionAudio(self):
		audios = Audio.objects.all()
		for a in audios:
			pond = 0.00
			cant = 0
			for r in Reporte.objects.filter(fk_audio=a):
				pond = pond + r.ponderacion
				cant += 1
			a.ponderacion = pond/cant
			a.save()
	
	def _cargarMetadatos(self):
		user ="tod"
		pw = "Tod2019*"
		fecha_desde=date.today().strftime("%y%m%d")
		fecha_hasta=date.today().strftime("%y%m%d")
		audios = Audio.objects.filter(procesado=False)
		count = 0
		for a in audios:
			try:
				idInteraccion = a.idInteraccion
				parameter = "store%3dREP_RDL_GrabacionesBasico%23%23idPermiso%3dREPORTES_Grabaciones_Grabaciones+B%c3%a1sico%23%23Version%3d13%23%23col%3d%23%23Idioma%3des%23%23SizeWeb%3d300%23%23SizePrint%3d29.7%7c%7c21%7c%7ccm%23%23Orientacion%3dH%23%23Ocultar%3d4%7c%7c%23%23OrderBy%3dStartRec%23A%7c%7c%23%23UserId%3d1701%23%23PEXT_TipoSalidaRep%3d0%23%23PEXT_Query%3d%23%23PEXT_WS%3d1%7c%7c%23%23RDLC_RowsByPage%3d-1%23%23PEXT_MaxRow%3d15000%23%23RDLC_FormInt%3d0%23%23RDLC_Culture%3des-AR%23%23RDLC_strDateFormat%3ddd%2fMM%2fyyyy%23%23PEXT_FechaRango%3d1234567%7c%7c"+fecha_desde+"%7c%7c"+fecha_hasta+"%23%23PEXT_idEmpresa%3d-1%23%23PEXT_idCamp%3d-1%23%23PEXT_idLote%3d-1%23%23PEXT_idGrupo%3d-1%23%23PEXT_idAgente%3d-1%23%23PEXT_idCliente%3d%23%23PEXT_Cliente%3d%23%23PEXT_MinDuracion%3d00%3a00%3a00%23%23PEXT_MaxDuracion%3d00%3a00%3a00%23%23PEXT_idCRM%3d%23%23PEXT_ResultadoGestion%3d-1%23%23PEXT_idInteraccion%3d"+idInteraccion+"%23%23PEXT_Extension%3d%23%23PEXT_idSentido%3d-1%23%23RDLC_TipoContacto%3d-1%23%23RDLC_newWin%3d%23%23RDLC_newTabExcel%3d%23%23RDLC_ChatCompleto%3d%23%23RDLC_MailCompleto%3d%23%23RDLC_EstiloRep%3d0%23%23RDLC_DocumentMap%3d%23%23RDLC_win_width%3d640%23%23RDLC_win_height%3d480%23%23HIDD_fromExecuteSQL%3d%23%23brw%3dChrome%23%23brwver%3d76%23%23"
				url = "http://mitrol.provincianet.com.ar/ws.asmx/MitrolWS_UserPass?Username="+user+"&Password="+pw+"&wsParameter="+parameter
				r = requests.get(url=url)
				s =BeautifulSoup(r.text,"lxml")
				agente = ""
				campaña = ""
				#Ver si existe agente, sino crearlo
				if Agente.objects.filter(idMitrol=s.idagente.contents[0]).exists():
					agente = Agente.objects.get(idMitrol=s.idagente.contents[0])
				else:
					agente = Agente(nombre=s.nombreagente.contents[0],idMitrol=s.idagente.contents[0])
					agente.save()
					
				#Ver si existe la campaña, sino crearlo
				if Campaña.objects.filter(idMitrol=s.idcampania.contents[0]).exists():
					campaña = Campaña.objects.get(idMitrol=s.idcampania.contents[0])
				else:
					campaña = Campaña(nombre=s.nombrecampania.contents[0],idMitrol=s.idcampania.contents[0])
					campaña.save()
					
				a.agente = agente
				a.campaña = campaña
				a.procesado = True
				a.save()
				count += 1
			except:
				pass
	
	def handle(self, *args, **options):
		self._cargarMetadatos()
