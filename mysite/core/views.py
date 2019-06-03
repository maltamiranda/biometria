import pdb, random, threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from django.template.loader import render_to_string

from .forms import AudioForm, FuncionForm, PalabraForm, Campaña_funcionesForm
from .models import Audio
from .models import Funcion
from .models import Reporte, Palabras, Campaña, Campaña_funciones, Campaña_Audio_Analisis
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
	

def background_analisis(audio, funcion, palabras):
	print ("inicio de analisis de" + str(audio.file))
	palabras_funcion = {}
	for m in palabras:
		palabras_funcion[str(m.palabra)] = int(m.porcentaje)
		
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
	print ("finalizo el reporte de" + str(audio.file))
	
@login_required
def analizar(request, pk):
	if request.method == 'POST':
		
		funcion_id = request.POST['post_funcion']
		audio_id = request.POST['post_audio']
		
		audio = Audio.objects.get(pk=audio_id)
		funcion = Funcion.objects.get(pk=funcion_id)
		palabras = Palabras.objects.filter(fk_funcion=1)
		t = threading.Thread(target=background_analisis, args=(), kwargs={"audio":audio, 
																			"funcion":funcion, 
																			"palabras":palabras})
		t.setDaemon(True)
		t.start()
		
		
		return redirect('audio_list')
	else:
		
		audio = Audio.objects.get(pk=pk)
		funcion = Funcion.objects.all()
		palabras = Palabras.objects.filter(fk_funcion=1)
		return render(request, 'analizar.html',{'audio':audio,
												'funcion':funcion,
												'palabras':palabras,})
	
@login_required
def reportes(request):
	reportes = Reporte.objects.all()
	return render(request, 'reportes.html', {'reportes':reportes})
	
@login_required
def reporte_generado(request, pk):
	reporte = Reporte.objects.get(pk=pk)
	return render(request, 'reporte_generado.html', {'reporte':reporte})

@login_required
def funciones_list(request):
	funcion = Funcion.objects.all()
	return render(request, 'funciones_list.html', {"funciones":funcion})

@login_required
def funciones_crear(request):
	if request.method == 'POST':
		form = FuncionForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('funciones_list')
	else:
		form = FuncionForm()
		return render(request, 'funciones_crear.html', {'form':form})


		
@login_required
def funciones_detalle(request, pk):
	funcion = Funcion.objects.get(pk=pk)
	palabras = Palabras.objects.filter(fk_funcion=funcion.id)
	return render(request,'funciones_detalle.html',{'funcion':funcion,'palabras':palabras})

	
@login_required
def guardar_palabra_form(request,pk_funcion, form, template_name):
	data = dict()
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			palabras = Palabras.objects.filter(fk_funcion=pk_funcion)
			data['html_tabla_palabras'] = render_to_string('includes/palabras_parcial_tabla.html', {
				'palabras': palabras})
		else:
			data['form_is_valid'] = False
	context = {'form':form,'pk_funcion':pk_funcion}
	data['html_form'] = render_to_string(template_name,context,request=request)
	return JsonResponse(data)
	
def actualizarPonderacionFuncion(pk_funcion):
	funcion = Funcion.objects.get(pk=pk_funcion)
	palabras = Palabras.objects.filter(fk_funcion=funcion.id)
	pond = 0
	for p in palabras:
		pond = pond + p.porcentaje
		
	funcion.ponderacion = pond
	if pond == 100:
		funcion.estado = 1
	else:
		funcion.estado = 2
	funcion.save()
	
@login_required
def crear_palabra(request, pk_funcion):
	data = dict()
	if request.method == 'POST':
		form = PalabraForm(request.POST,fk_funcion=pk_funcion)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			palabras = Palabras.objects.filter(fk_funcion=pk_funcion)
			data['html_tabla_palabras'] = render_to_string('includes/palabras_parcial_tabla.html', {
				'palabras': palabras})
			actualizarPonderacionFuncion(pk_funcion)
		else:
			data['form_is_valid'] = False
	else:
		form = PalabraForm(fk_funcion=pk_funcion)
	context = {'form':form,'pk_funcion':pk_funcion}
	data['html_form'] = render_to_string('includes/palabra_parcial_crear.html',context,request)
	
	funcion = Funcion.objects.get(pk=pk_funcion)
	data['html_funcion'] = render_to_string('includes/funcion_parcial_detalle.html',{'funcion':funcion},request)
	
	return JsonResponse(data)
	
	
	
@login_required
def editar_palabra(request, pk_funcion, pk_palabra):
	data = dict()
	palabra = get_object_or_404(Palabras, pk=pk_palabra)
	if request.method == 'POST':
		form = PalabraForm(request.POST,fk_funcion=pk_funcion, instance=palabra)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			palabras = Palabras.objects.filter(fk_funcion=pk_funcion)
			data['html_tabla_palabras'] = render_to_string('includes/palabras_parcial_tabla.html', {
				'palabras': palabras})
			actualizarPonderacionFuncion(pk_funcion)
	else:
		form = PalabraForm(fk_funcion=pk_funcion, instance=palabra)
	
	context = {'form':form,'pk_funcion':pk_funcion,'pk_palabra':pk_palabra}
	data['html_form'] = render_to_string('includes/palabra_parcial_update.html',context,request)
	
	funcion = Funcion.objects.get(pk=pk_funcion)
	data['html_funcion'] = render_to_string('includes/funcion_parcial_detalle.html',{'funcion':funcion},request)
	
	return JsonResponse(data)
	
@login_required
def borrar_palabra(request,pk_funcion,pk_palabra):
	data = dict()
	palabra = get_object_or_404(Palabras, pk=pk_palabra)
	if request.method == 'POST':
		palabra.delete()
		data['form_is_valid'] = True  # This is just to play along with the existing code
		palabras = Palabras.objects.filter(fk_funcion=pk_funcion)
		data['html_tabla_palabras'] = render_to_string('includes/palabras_parcial_tabla.html', {
				'palabras': palabras})
		actualizarPonderacionFuncion(pk_funcion)
	else:
		context = {'palabra':palabra,'pk_funcion':pk_funcion,'pk_palabra':pk_palabra}
		data['html_form'] = render_to_string('includes/palabra_parcial_borrar.html',context,request)
	
	funcion = Funcion.objects.get(pk=pk_funcion)
	data['html_funcion'] = render_to_string('includes/funcion_parcial_detalle.html',{'funcion':funcion},request)
	
	
	return JsonResponse(data)
	
	
@login_required
def cargar_funcion_descripcion(request):
	id = request.POST['funcion_id']
	data = {
		'descripcion': Funcion.objects.get(pk=id).descripcion
	}
	return JsonResponse(data)
	
	
@login_required
def campañas(request):
	campañas = Campaña.objects.all()
	return render(request, 'campaña_list.html', {'campañas':campañas})
	
@login_required
def campañas_detalle(request, pk_campaña):
	campaña = get_object_or_404(Campaña, pk=pk_campaña)
	campaña_funciones = Campaña_funciones.objects.filter(fk_campaña=campaña)
	return render(request, 'campaña_detalle.html', {'campaña_funciones':campaña_funciones,'campaña_nombre':campaña.nombre, 'campaña_id':campaña.id})
	

def background_analisis_campaña(campaña, campaña_funcion_creada):
	audios = Audio.objects.filter(campaña=campaña)
	funciones = campaña_funcion_creada.funciones.all()
	
	for a in audios:
		for f in funciones:
			e = Evaluador()
			#ch1 = e.normalizar(a.canal_1) 
			suma = e.ponderizar(a.canal_1.lower(), Palabras.objects.filter(fk_funcion=f))
			
			#analisis = random.randint(0, 100)
			Campaña_Audio_Analisis.objects.create(analisis=suma, fk_audio=a, fk_campaña_funcion=campaña_funcion_creada, fk_campaña=campaña, fk_funcion=f)
	
@login_required
def capañas_detalle_crear(request, pk_campaña):
	if request.method == 'POST':
		form = Campaña_funcionesForm(request.POST,fk_campaña=pk_campaña)
		if form.is_valid():
			campaña_funcion_creada = form.save()
			campaña = get_object_or_404(Campaña, pk=pk_campaña)
			campaña_funciones = Campaña_funciones.objects.filter(fk_campaña=campaña)
			
			
			#background_analisis_campaña(campaña,campaña_funcion_creada)
			t = threading.Thread(target=background_analisis_campaña, args=(), kwargs={"campaña":campaña, "campaña_funcion_creada":campaña_funcion_creada})
			t.setDaemon(True)
			t.start()
			
			campaña_funciones = Campaña_funciones.objects.filter(fk_campaña=campaña)
			return render(request, 'campaña_detalle.html', {'campaña_funciones':campaña_funciones,'campaña_nombre':campaña.nombre, 'campaña_id':campaña.id})
	else:
		form = Campaña_funcionesForm(fk_campaña=pk_campaña)
		return render(request, 'campaña_detalle_crear.html', {'form':form})
		
@login_required
def campaña_funcion_analisis(request, pk_campaña, pk_campaña_funcion):
	campaña =get_object_or_404(Campaña, pk=pk_campaña)
	campaña_funcion = get_object_or_404(Campaña_funciones, pk=pk_campaña_funcion)
	campaña_funcion_analisis = Campaña_Audio_Analisis.objects.filter(fk_campaña=campaña,fk_campaña_funcion=campaña_funcion)
	return render(request, 'campaña_audio_analisis.html',{'campaña_funcion_analisis':campaña_funcion_analisis})
	
def funciones_borrar(request, pk):
	if request.method == 'POST':
		funcion = Funcion.objects.get(pk=pk)
		funcion.delete()
		
	return redirect('funciones_list')
	
@login_required
def transcripcion(request, pk_campaña, pk_campaña_funcion, pk_audio):
	audio = Audio.objects.get(pk=pk_audio)
	return render(request, 'transcripcion.html', {'audio':audio})