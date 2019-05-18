import pdb, random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from .forms import AudioForm
from .models import Audio
from .models import Funcion
from .models import Reporte, Palabras
from .transcriptor import Transcriptor
from .ponderacion import Evaluador


def home(request):
	count = User.objects.count()
	return 	render(request, 'home.html', {'count':count}
		)

def singup(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			redirect('home')
	else:
		form = UserCreationForm()
	return render(request, 'registration/singup.html', {
		'form' : form
		})
	
@login_required
def funciones(request):
	return render(request, 'funciones.html')


@login_required
def test(request):
	return render(request, 'test.html')

@login_required
def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'upload.html', context)

@login_required
def audio_list(request):
	audios = Audio.objects.all()
	return render(request, 'audio_list.html', {'audios':audios})

@login_required
def upload_audio(request):
	if request.method == 'POST':
		form = AudioForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('audio_list')
	else:
		form = AudioForm()
	return render(request, 'upload_audio.html', {'form':form})


def delete_audio(request, pk):
	if request.method == 'POST':
		audio = Audio.objects.get(pk=pk)
		audio.delete()
		
	return redirect('audio_list')

@login_required
def download(request):
	return render(request, 'download.html')


	
@login_required
def secret_page(request):
	return render(request, 'secret_page.html')
	

@login_required
def analizar(request, pk):
	if request.method == 'POST':
		funcion_id = request.POST['post_funcion']
		audio_id = request.POST['post_audio']
		
		audio = Audio.objects.get(pk=audio_id)
		funcion = Funcion.objects.get(pk=funcion_id)
		palabras = Palabras.objects.filter(fk_funcion=1)
		palabras_funcion = []
		for m in palabras:
			palabras_funcion.append((m.palabra, m.porcentaje))
			
		t = Transcriptor()
		c1, c2 = t.parse(audio.file)

		e = Evaluador()
		ch1 = e.normalizar(c1) 
		ch2 = e.normalizar(c2) 

		suma = e.calificar(ch1, palabras_funcion, funcion.frase)
		
		reporte = Reporte.objects.create(
			ponderacion = suma,
			fk_funcion = funcion,
			fk_audio = audio,
			canal_1 = ch1,
			canal_2 = ch2,
			nombre = funcion.nombre,
			nombre_audio = audio.file
		)
		
		return redirect('audio_list')
	else:
		
		audio = Audio.objects.get(pk=pk)
		funcion = Funcion.objects.all()
		palabras = Palabras.objects.filter(fk_funcion=1)
		return render(request, 'analizar.html',{'audio':audio,
												'funcion':funcion,
												'palabras':palabras})
	
@login_required
def reportes(request):
	reportes = Reporte.objects.all()
	return render(request, 'reportes.html', {'reportes':reportes})
	
@login_required
def reporte_generado(request, pk):
	reporte = Reporte.objects.get(pk=pk)
	return render(request, 'reporte_generado.html', {'reporte':reporte})

@login_required
def cargar_funcion_descripcion(request):
	id = request.POST['funcion_id']
	data = {
		'descripcion': Funcion.objects.get(pk=id).descripcion
	}
	return JsonResponse(data)