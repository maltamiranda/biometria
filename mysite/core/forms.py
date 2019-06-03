from django import forms

from .models import Audio, Funcion, Palabras, Campaña_funciones, Campaña


class AudioForm(forms.ModelForm):
	class Meta:
		model = Audio
		fields = ('id','file')

		
class FuncionForm(forms.ModelForm):
	class Meta:
		model = Funcion
		fields = ('nombre', 'descripcion')
		
class PalabraForm(forms.ModelForm):
	class Meta:
		model = Palabras
		fields = ('palabra','porcentaje', "fk_funcion")
	
	#def is_valid(self,):
	#	return not Palabras.objects.filter(palabra=self.fields['palabra'],fk_funcion=self.fk_funcion).exists()
		
	def __init__(self, *args, **kwargs):
		fk_funcion = kwargs.pop('fk_funcion','')
		super(PalabraForm, self).__init__(*args, **kwargs)
		self.fields['fk_funcion']=forms.ModelChoiceField(queryset=Funcion.objects.filter(id=fk_funcion))
		
class Campaña_funcionesForm(forms.ModelForm):
	class Meta:
		model = Campaña_funciones
		fields = ('funciones','fk_campaña')
		
	def __init__(self, *args, **kwargs):
		fk_campaña = kwargs.pop('fk_campaña','')
		super(Campaña_funcionesForm, self).__init__(*args, **kwargs)
		self.fields['fk_campaña']=forms.ModelChoiceField(queryset=Campaña.objects.filter(id=fk_campaña))