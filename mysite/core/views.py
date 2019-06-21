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

#group required
from django.utils import six
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

#decorator
def group_required(group, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a group permission,
    redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        if isinstance(group, six.string_types):
            groups = (group, )
        else:
            groups = group
        # First check if the user has the permission (even anon users)

        if user.groups.filter(name__in=groups).exists():
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url)

def home(request):
	count = User.objects.count()
	return 	render(request, 'home.html', {'count':count}
		)
	
@login_required
def funciones(request):
	return render(request, 'funciones.html')


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
	
@group_required(('Auditor Reportes', '/accounts/login/'))
def reportes(request):
	campaña_funcion_analisis = Campaña_Audio_Analisis.objects.all()
	
	campañas = {}
	campañasList = []
	for camp in campaña_funcion_analisis:
		campTemp = campañas.get(camp.fk_audio.idInteraccion, None)
		if campTemp == None:
			campañas[camp.fk_audio.idInteraccion] = [camp.analisis,camp.fk_audio.agente.nombre,1, camp.fk_audio.inicio]
		else:
			analisis = campTemp[0] +  camp.analisis
			cont = campTemp[2] + 1
			campañas[camp.fk_audio.idInteraccion] = [analisis,camp.fk_audio.agente.nombre, cont, camp.fk_audio.inicio]
	for key in campañas:
		temp = campañas[key]
		campañasList.append({'analisis':round(temp[0]/temp[2],1),'nombreAgente':temp[1], 'audio':key, 'fecha':temp[3]})
	return render(request, 'reportes.html', {'campañas':campañasList})
	
def detalleAnalisis(request, audio):
	data = dict()
	a = get_object_or_404(Audio, idInteraccion=audio)
	print (a)
	audios = Campaña_Audio_Analisis.objects.filter(fk_audio_id=a.id)
	
	data['html_funcion'] = render_to_string('includes/detalleAnalisis_parcial.html',{'audios':audios},request)
	
	return JsonResponse(data)
	
@login_required
def reporte_generado(request, pk):
	reporte = Reporte.objects.get(pk=pk)
	return render(request, 'reporte_generado.html', {'reporte':reporte})

@group_required(('Auditor Funciones', '/accounts/login/'))
#@login_required
def funciones_list(request):
	funcion = Funcion.objects.all()
	return render(request, 'funciones_list.html', {"funciones":funcion})

@group_required(('Auditor Funciones', '/accounts/login/'))
#@login_required
def funciones_crear(request):
	if request.method == 'POST':
		form = FuncionForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('funciones_list')
	else:
		form = FuncionForm()
		return render(request, 'funciones_crear.html', {'form':form})

@group_required(('Auditor Funciones', '/accounts/login/'))
#@login_required
def funciones_detalle(request, pk):
	funcion = Funcion.objects.get(pk=pk)
	palabras = Palabras.objects.filter(fk_funcion=funcion.id)
	return render(request,'funciones_detalle.html',{'funcion':funcion,'palabras':palabras})

@group_required(('Auditor Funciones', '/accounts/login/'))
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
	
@group_required(('Auditor Funciones', '/accounts/login/'))
def crear_palabra(request, pk_funcion):
	data = dict()
	if request.method == 'POST':
		form = PalabraForm(request.POST,initial={'fk_funcion':pk_funcion})
		print (form)
		print (form.instance.fk_funcion)
		form.instance.fk_funcion=Funcion.objects.get(id=pk_funcion)
		print (form.instance.fk_funcion)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			palabras = Palabras.objects.filter(fk_funcion=pk_funcion)
			funcion = Funcion.objects.get(pk=pk_funcion)
			data['html_tabla_palabras'] = render_to_string('includes/palabras_parcial_tabla.html', {
				'palabras': palabras, 'funcion':funcion})
			actualizarPonderacionFuncion(pk_funcion)
		else:
			data['form_is_valid'] = False
	else:
		form = PalabraForm(initial={'fk_funcion':pk_funcion})
	context = {'form':form,'pk_funcion':pk_funcion}
	data['html_form'] = render_to_string('includes/palabra_parcial_crear.html',context,request)
	
	funcion = Funcion.objects.get(pk=pk_funcion)
	data['html_funcion'] = render_to_string('includes/funcion_parcial_detalle.html',{'funcion':funcion},request)
	
	return JsonResponse(data)
	
	
	
@group_required(('Auditor Funciones', '/accounts/login/'))
def editar_palabra(request, pk_funcion, pk_palabra):
	data = dict()
	palabra = get_object_or_404(Palabras, pk=pk_palabra)
	if request.method == 'POST':
		form = PalabraForm(request.POST, instance=palabra)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			palabras = Palabras.objects.filter(fk_funcion=pk_funcion)
			funcion = Funcion.objects.get(pk=pk_funcion)
			data['html_tabla_palabras'] = render_to_string('includes/palabras_parcial_tabla.html', {
				'palabras': palabras, 'funcion':funcion})
			actualizarPonderacionFuncion(pk_funcion)
	else:
		form = PalabraForm(instance=palabra)
	
	context = {'form':form,'pk_funcion':pk_funcion,'pk_palabra':pk_palabra}
	data['html_form'] = render_to_string('includes/palabra_parcial_update.html',context,request)
	
	funcion = Funcion.objects.get(pk=pk_funcion)
	data['html_funcion'] = render_to_string('includes/funcion_parcial_detalle.html',{'funcion':funcion},request)
	
	return JsonResponse(data)
	
@group_required(('Auditor Funciones', '/accounts/login/'))
def borrar_palabra(request,pk_funcion,pk_palabra):
	data = dict()
	palabra = get_object_or_404(Palabras, pk=pk_palabra)
	if request.method == 'POST':
		palabra.delete()
		data['form_is_valid'] = True  # This is just to play along with the existing code
		palabras = Palabras.objects.filter(fk_funcion=pk_funcion)
		funcion = Funcion.objects.get(pk=pk_funcion)
		data['html_tabla_palabras'] = render_to_string('includes/palabras_parcial_tabla.html', {
				'palabras': palabras, 'funcion':funcion})
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
	
	
@group_required(('Auditor Campañas', '/accounts/login/'))
def campañas(request):
	campañas = Campaña.objects.all()
	return render(request, 'campaña_list.html', {'campañas':campañas})
	
@group_required(('Auditor Campañas', '/accounts/login/'))
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
	
@group_required(('Auditor Campañas', '/accounts/login/'))
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
		
@group_required(('Auditor Campañas', '/accounts/login/'))
def campaña_funcion_analisis(request, pk_campaña, pk_campaña_funcion):
	campaña =get_object_or_404(Campaña, pk=pk_campaña)
	campaña_funcion = get_object_or_404(Campaña_funciones, pk=pk_campaña_funcion)
	campaña_funcion_analisis = Campaña_Audio_Analisis.objects.filter(fk_campaña=campaña,fk_campaña_funcion=campaña_funcion)
	return render(request, 'campaña_audio_analisis.html',{'campaña_funcion_analisis':campaña_funcion_analisis})

@group_required(('Auditor Funciones', '/accounts/login/'))
def funciones_borrar(request, pk):
	if request.method == 'POST':
		funcion = Funcion.objects.get(pk=pk)
		funcion.delete()
	return redirect('funciones_list')
	
@group_required(('Auditor Campañas', '/accounts/login/'))
def transcripcion(request, pk_campaña, pk_campaña_funcion, pk_audio):
	audio = Audio.objects.get(pk=pk_audio)
	return render(request, 'transcripcion.html', {'audio':audio})
	
def reproducir(request, pk):
	return render(request,'reproducir.html')
	
def cambiarEstado(request, pk_funcion):
	data = dict()
	funcion = Funcion.objects.get(id=pk_funcion)
	if funcion.estado == 1:
		funcion.estado = 2
		funcion.save()
		data['estado']='disable'
		data['is_valid']=True
	else:
		if funcion.ponderacion == 100:
			funcion.estado = 1
			funcion.save()
			data['estado']='enable'
			data['is_valid']=True
		else:
			data['is_valid']=False
		
	return JsonResponse(data)
	
	
	





