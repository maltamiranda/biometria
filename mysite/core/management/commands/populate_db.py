from django.core.management.base import BaseCommand
from mysite.core.models import Audio, Agente, Campaña, Funcion, Palabras, Reporte
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
    
    def _cargarReportes(self):
        audios = Audio.objects.all()
        for a in audios:
            try:
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
            except:
                    pass


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
        
        Audio.objects.create(file="audios/files/llamado4_1.wav",inicio=datetime.strptime("01/03/2019 8:01", "%d/%m/%Y %H:%M"), idInteraccion="a80984_2_190301080014748_IVR_06040", agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
        Audio.objects.create(file="audios/files/a83333_2_181111150759852_IVR_07040.wav",inicio=datetime.strptime("01/03/2019 8:06", "%d/%m/%Y %H:%M"), idInteraccion="a80984_2_190301080607954_IVR_07040", agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
        Audio.objects.create(file="audios/files/a83410_2_181111103241388_IVR_06040.wav",inicio=datetime.strptime("01/03/2019 8:15", "%d/%m/%Y %H:%M"), idInteraccion="a80984_2_190301081356154_IVR_06040", agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
        Audio.objects.create(file="audios/files/a83927_2_181112080250192_IVR_01003.wav",inicio=datetime.strptime("01/03/2019 8:41", "%d/%m/%Y %H:%M"), idInteraccion="a80984_2_190301084012517_IVR_07040", agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
        Audio.objects.create(file="audios/files/a83996_2_181111192011982_IVR_02140.wav",inicio=datetime.strptime("01/03/2019 8:47", "%d/%m/%Y %H:%M"), idInteraccion="a80984_2_190301084606786_IVR_01040", agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
        Audio.objects.create(file="audios/files/a89237_2_181111124023801_IVR_03151.wav",inicio=datetime.strptime("01/03/2019 8:54", "%d/%m/%Y %H:%M"), idInteraccion="a80984_2_190301085405392_IVR_07042", agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
        Audio.objects.create(file="audios/files/llamado_provincia.wav",inicio=datetime.strptime("01/03/2019 8:57", "%d/%m/%Y %H:%M"), idInteraccion="a80984_2_190301085653361_IVR_07040", agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
        Audio.objects.create(file="audios/files/llamado_provincia_extenso.wav",inicio=datetime.strptime("01/03/2019 9:02", "%d/%m/%Y %H:%M"), idInteraccion="a80984_2_190301090132123_IVR_06041", agente=Agente.objects.get(nombre="Sanmarco Jonatan Pablo Ivan"), campaña=Campaña.objects.get(nombre="Mesa Ayuda Banca Internet"))
    
    def _cargarPonderacionAudio(self):
        audios = Audio.objects.all()
        for a in audios:
            pond = 0.00
            cant = 0
            for r in Reporte.objects.filter(fk_audio=a):
                pond = pond + r.ponderacion
                cant += 1
            if cant != 0:
                a.ponderacion = pond/cant
            a.save()

    def handle(self, *args, **options):
        #self._cargarAudios()
        #self._cargarTranscripciones()
        self._cargarReportes()
        self._cargarPonderacionAudio()
