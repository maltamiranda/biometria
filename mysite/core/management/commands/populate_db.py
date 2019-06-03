from django.core.management.base import BaseCommand
from mysite.core.models import Audio, Agente, Campaña
import os
from datetime import datetime
from mysite.core.transcriptor import Transcriptor
from mysite.core.ponderacion import Evaluador

class Command(BaseCommand):
	args = '<foo bar ...>'
	help = 'our help string comes here'
	#path = 'M:\FreeLance\18-05\static\media\audios\files'
	path = 'M:\\FreeLance\\18-05\\static\\media\\audios\\files'
	cantidad = ''
	
	#def _cargarCampañas(self):
	#
	#def _cargarAgentes(self):
	
	def _cargarAudios(self):
		
		for r, d, f in os.walk(self.path):
			for file in f:
				if '.wav' in file:
					print (file)
					audio = Audio.objects.create(file=("audios/files/"+file), inicio=datetime.strptime("01/03/2019 8:06", "%d/%m/%Y %H:%M"), idInteraccion=file, agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
					
					t = Transcriptor()
					e = Evaluador()
					c1, c2 = t.parse(audio.file)
					ch1 = e.normalizar(c1) 
					ch2 = e.normalizar(c2)
					audio.canal_1 = ch1
					audio.canal_2 = ch2
					audio.save()
	
	def handle(self, *args, **options):
		self._cargarAudios()
		
