from django import forms

from .models import Audio, Funcion, Palabras, Analisis, Campaña


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
		fields = ('palabra','porcentaje','fk_funcion')
		widgets = {'fk_funcion': forms.HiddenInput()}
		
class AnalisisForm(forms.ModelForm):
	#widgets={'funciones':forms.CheckboxSelectMultiple}
	class Meta:
		model = Analisis
		fields = ('funciones','fk_campaña')
		widgets = {'fk_campaña': forms.HiddenInput()}
		
	#def __init__(self, *args, **kwargs):
	#	fk_campaña = kwargs.pop('fk_campaña','')
	#	super(Campaña_funcionesForm, self).__init__(*args, **kwargs)
	#	self.fields['fk_campaña']=forms.ModelChoiceField(queryset=Campaña.objects.filter(id=fk_campaña))
        