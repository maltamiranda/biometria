from django.db import models


class Audio(models.Model):
    file = models.FileField(upload_to='audios/files/')

    def __str__(self):
        #return self.title
        return str(self.file)


    def delete(self, *args):
        self.file.delete()
        super().delete(*args)

class Funcion(models.Model):
	nombre = models.CharField(max_length=30, unique=True)
	descripcion = models.CharField(max_length=255)
	frase = models.CharField(max_length=255)
	def __str__(self):
		return self.nombre

class Palabras(models.Model):
	fk_funcion = models.ForeignKey(Funcion, related_name='funcion', on_delete=models.CASCADE)
	palabra = models.CharField(max_length=30, unique=True)
	porcentaje = models.IntegerField(default=5)
	
	class Meta:
		unique_together = (("fk_funcion", "palabra"),)
		
	def __str__(self):
		return self.palabra
		
class Reporte(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	ponderacion = models.IntegerField()
	fk_funcion = models.ForeignKey(Funcion, related_name='funcion_reporte', on_delete=models.CASCADE)
	fk_audio = models.ForeignKey(Audio, related_name='audio', on_delete=models.CASCADE)
	canal_1 = models.TextField()
	canal_2 = models.TextField()
	nombre = models.CharField(max_length=255)
	nombre_audio = models.CharField(max_length=255)
	
	def __str__(self):
		return self.nombre