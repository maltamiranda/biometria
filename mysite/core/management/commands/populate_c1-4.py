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
	path = '/home/ubuntu/biometria/biometria/static/media/audios/files'
	cantidad = ''
	
	#def _cargarCampañas(self):
	#
	#def _cargarAgentes(self):
	
	def _cargarTranscripciones(self):
		for camp in ["DP_Emerix ADM Publica","DP Emerix B","DP Emerix A","Mesa Ayuda Banca Interne"]:
			for audio in Audio.objects.filter(campaña__nombre=camp):
				t = Transcriptor()
				e = Evaluador()
				c1, c2 = t.parse(audio.file)
				ch1 = e.normalizar(c1) 
				ch2 = e.normalizar(c2)
				audio.canal_1 = ch1
				audio.canal_2 = ch2
				audio.save()
	
	def handle(self, *args, **options):

		self._cargarTranscripciones()
		
		
