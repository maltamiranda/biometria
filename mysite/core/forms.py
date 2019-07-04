from django import forms

from .models import Audio, Funcion, Palabras, Campaña, Reporte


class AudioForm(forms.ModelForm):
	class Meta:
		model = Audio
		fields = ('id','file')

class ComentarioAudioForm(forms.ModelForm):
	class Meta:
		model = Audio
		fields = ('comentario','id')

class ComentarioReporteForm(forms.ModelForm):
	class Meta:
		model = Reporte
		fields = ('comentario','id')

		
class FuncionForm(forms.ModelForm):
	class Meta:
		model = Funcion
		fields = ('nombre', 'descripcion')
		
class PalabraForm(forms.ModelForm):
	class Meta:
		model = Palabras
		fields = ('palabra','porcentaje','fk_funcion')
		widgets = {'fk_funcion': forms.HiddenInput()}
		
#class AnalisisForm(forms.ModelForm):
	#widgets={'funciones':forms.CheckboxSelectMultiple}
#	class Meta:
#		model = Analisis
#		fields = ('funciones','fk_campaña')
#		widgets = {'fk_campaña': forms.HiddenInput()}

class CampañaFuncionForm(forms.ModelForm):
	class Meta:
		model = Campaña
		fields = ('fk_funciones',)