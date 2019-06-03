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
	
	def _cargarCampañas(self):
		Campaña.objects.create(nombre="DP_Emerix ADM Publica")
		Campaña.objects.create(nombre="DP Emerix B")
		Campaña.objects.create(nombre="DP Emerix A")
		Campaña.objects.create(nombre="Mesa Ayuda Banca Internet")
		Campaña.objects.create(nombre="Seguros At Cliente")
		Campaña.objects.create(nombre="Reclamos")
		Campaña.objects.create(nombre="PNET Mesa Funcional - MDA")
		Campaña.objects.create(nombre="Paquetes ENTRANTE CLIENTES")
		Campaña.objects.create(nombre="RENAPER")
		Campaña.objects.create(nombre="Banco")
		Campaña.objects.create(nombre="Seguros SuperIntendencia")
		Campaña.objects.create(nombre="Opcion Premios")
		Campaña.objects.create(nombre="Out Traslados")
		Campaña.objects.create(nombre="ART_TRASLADOS")
		Campaña.objects.create(nombre="ART_PRACTICAS_MEDICAS_TURNOS")
		Campaña.objects.create(nombre="Productos y Servicios")
		Campaña.objects.create(nombre="Seguros Siniestros")
		Campaña.objects.create(nombre="Out_ART traslados y encuestas")
		Campaña.objects.create(nombre="ART At Cliente 3436 ENTRANTE DESDE CEM")
		Campaña.objects.create(nombre="ART_OTRAS_CONSULTAS")
		Campaña.objects.create(nombre="E-Provincia Bapro")
		Campaña.objects.create(nombre="Autogestion_IN_SinURL")
		Campaña.objects.create(nombre="Seguros VDT")
		Campaña.objects.create(nombre="Mesa ayuda BIP empresas")
		Campaña.objects.create(nombre="ART_PAGOS_REINTEGROS")
		Campaña.objects.create(nombre="Mora entrantes 0810-222-6672")
		Campaña.objects.create(nombre="Seguros Productores")
		Campaña.objects.create(nombre="ART_COMERCIAL_EMPRESAS")
		Campaña.objects.create(nombre="OpenSport")
		Campaña.objects.create(nombre="Desborde VDT")
		Campaña.objects.create(nombre="Desborde_Mora")
		Campaña.objects.create(nombre="MicroCreditos")
		Campaña.objects.create(nombre="Out_OpenSport")
		Campaña.objects.create(nombre="Out_Centro de recarga")
		Campaña.objects.create(nombre="Hipotecario Validado")
		Campaña.objects.create(nombre="Out_Sony")
		Campaña.objects.create(nombre="ATOS IMED")
		Campaña.objects.create(nombre="Seguros Inspecciones")
		Campaña.objects.create(nombre="RIESGO_114649-8400")
		Campaña.objects.create(nombre="Hipotecario Sin Validar")
		Campaña.objects.create(nombre="Out_Seguros VDT")
		Campaña.objects.create(nombre="Out_MicroCreditos")
		Campaña.objects.create(nombre="ART Conmutador")
		Campaña.objects.create(nombre="SONY_VENTAS")
		Campaña.objects.create(nombre="Sony_Consulta")
		Campaña.objects.create(nombre="OUT Actualización de Datos")
		Campaña.objects.create(nombre="Out_PROVINCIA NET PPAL")
		Campaña.objects.create(nombre="LLaCo_01-90")
		Campaña.objects.create(nombre="ART At Cliente 3417")
		Campaña.objects.create(nombre="Hipotecarios Salientes")
		Campaña.objects.create(nombre="Autogestion_IN")
		Campaña.objects.create(nombre="RIESGO_0800-777-7663")
		Campaña.objects.create(nombre="Sony_Atencion_clientes")
		Campaña.objects.create(nombre="Seguros Clientes BPBA")
		Campaña.objects.create(nombre="Out_Seguros At Clientes")
		Campaña.objects.create(nombre="DP_Devolucion Llamada BIP")
		Campaña.objects.create(nombre="Formularios Facebook")
		Campaña.objects.create(nombre="Retención de Clientes")
		Campaña.objects.create(nombre="Alta de Paquetes - BIP")
		Campaña.objects.create(nombre="Out_ART Morosos")
		Campaña.objects.create(nombre="Bienvenida - Paquetes")
		Campaña.objects.create(nombre="Copre")

	
	def handle(self, *args, **options):
		self._cargarCampañas()
		
