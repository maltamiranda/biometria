import pdb, random, threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect

import os

from .filters import ReporteFilter

from django.template.loader import render_to_string

from .forms import AudioForm, FuncionForm, PalabraForm, ComentarioReporteForm, ComentarioAudioForm, CampañaFuncionForm
from .models import Audio
from .models import Funcion
from .models import Reporte, Palabras, Campaña, Agente
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
	audios = Audio.objects.all()
	reporte_filter = ReporteFilter(request.GET, queryset=audios)
	return render(request, 'buscar.html',{'filter': reporte_filter})
#def reportes(request):
#	audios = Audio.objects.all()
#	return render(request, 'reportes.html', {'audios':audios})
	
def detalleAnalisis(request, audio):
	data = dict()
	a = get_object_or_404(Audio, idInteraccion=audio)
	reportes = Reporte.objects.filter(fk_audio=a.id)

	data['html_funcion'] = render_to_string('includes/detalleAnalisis_parcial.html',{'reportes':reportes},request)
	
	return JsonResponse(data)
	
@login_required
def reporte_generado(request, pk_reporte):
    reporte = Reporte.objects.get(pk=pk_reporte)
    audio = Audio.objects.get(pk=reporte.fk_audio.pk)
    campaña =get_object_or_404(Campaña, pk=audio.campaña.pk)
    palabras = Palabras.objects.filter(fk_funcion=reporte.fk_funcion)

    #Generar tabla con el texto trascripto
    contador = 0
    trans = []
    c1 = reporte.canal_1.split("|")
    c2 = reporte.canal_2.split("|")

    if len(c1) == len(c2):
        for i in range(len(c1)):
            trans.append([str(contador) + "-" + str(contador+30),
                            c1[i],
                            c2[i]])
            contador += 30

    return render(request, 'reporte_generado.html', {'reporte':reporte,
													'campaña':campaña,
													'palabras':palabras,
                                                    'trans':trans})

@group_required(('Auditor Funciones', '/accounts/login/'))
def funciones_list(request):
	funcion = Funcion.objects.all()
	return render(request, 'funciones_list.html', {"funciones":funcion})

@group_required(('Auditor Funciones', '/accounts/login/'))
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
	if pond != 100:
		funcion.estado = 2
	
	funcion.save()
	
@group_required(('Auditor Funciones', '/accounts/login/'))
def crear_palabra(request, pk_funcion):
	data = dict()
	if request.method == 'POST':
		form = PalabraForm(request.POST,initial={'fk_funcion':pk_funcion})
		form.instance.fk_funcion=Funcion.objects.get(id=pk_funcion)
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
	
@group_required(('Auditor Funciones', '/accounts/login/'))
def borrar_funcion(request,pk_funcion):
	data = dict()
	funcion = get_object_or_404(Funcion, pk=pk_funcion)
	if request.method == 'POST':
		funcion.delete()
		data['form_is_valid'] = True  # This is just to play along with the existing code
		funciones = Funcion.objects.all()
		data['html_tabla_funciones'] = render_to_string('includes/funcion_parcial_tabla.html', {
				'funciones': funciones})
	else:
		context = {'funcion':funcion,'pk_funcion':pk_funcion}
		data['html_form'] = render_to_string('includes/funcion_parcial_borrar.html',
		context,request)
	
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
	campañas = Campaña.objects.all().order_by('nombre')
	return render(request, 'campaña_list.html', {'campañas':campañas})
	
@group_required(('Auditor Campañas', '/accounts/login/'))
def campañas_detalle(request, pk_campaña):
    campaña = get_object_or_404(Campaña, pk=pk_campaña)
    if request.method == 'POST':
        campaña.fk_funciones.clear()
        funciones = request.POST.getlist('funciones')
        for f in funciones:
            func = Funcion.objects.get(id=f)
            campaña.fk_funciones.add(func)
            campaña.save()
        return redirect('campañas')
        
    funciones = Funcion.objects.filter(estado=1)
    funciones = funciones.difference(campaña.fk_funciones.all())
    return render(request, 'campaña_funcion.html', {'campaña':campaña,'funciones':funciones})
	
@group_required(('Auditor Campañas', '/accounts/login/'))
def configCampañaFunciones(request,pk_campaña):
	data = dict()
	campaña = get_object_or_404(Campaña, pk=pk_campaña)
	if request.method == 'POST':
		form = CampañaFuncionForm(request.POST, instance=campaña)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			campañas = Campaña.objects.all().order_by('nombre')
			data["html_tabla_campañas"] = render_to_string('includes/campaña_parcial_tabla.html', {
				'campañas': campañas})
	else:
		form = CampañaFuncionForm(instance=campaña)

	context = {'form':form,'campaña':campaña}
	data['html_form'] = render_to_string('includes/campaña_parcial_update.html',context,request)

	return JsonResponse(data)

def background_analisis_campaña(campaña, analisis_creado):
	audios = Audio.objects.filter(campaña=campaña)
	funciones = analisis_creado.funciones.all()
	for a in audios:
		for f in funciones:
			e = Evaluador()
			#ch1 = e.normalizar(a.canal_1) 
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
									fk_analisis=analisis_creado, 
									fk_funcion=f,
									canal_1=canal_1_resaltado,
									canal_2=a.canal_2,
									nombre_agente = a.agente.nombre,
									nombre_audio = a.idInteraccion,
									nombre_campaña = a.campaña.nombre,
									fecha_audio = a.inicio)
	
@group_required(('Auditor Campañas', '/accounts/login/'))
def capañas_detalle_crear(request, pk_campaña):
	if request.method == 'POST':
		form = AnalisisForm(request.POST,initial={'fk_campaña':pk_campaña})
		if form.is_valid():
			analisis_creado = form.save()
			campaña = get_object_or_404(Campaña, pk=pk_campaña)
			analisis = Analisis.objects.filter(fk_campaña=campaña)
			
			
			#background_analisis_campaña(campaña,campaña_funcion_creada)
			t = threading.Thread(target=background_analisis_campaña, args=(), kwargs={"campaña":campaña, "analisis_creado":analisis_creado})
			t.setDaemon(True)
			t.start()
			
			analisis = Analisis.objects.filter(fk_campaña=campaña)
			return render(request, 'campaña_detalle.html', {'analisis':analisis,'campaña_nombre':campaña.nombre, 'campaña_id':campaña.id})
	else:
		campaña = get_object_or_404(Campaña, pk=pk_campaña)
		form = AnalisisForm(initial={'fk_campaña':pk_campaña})
		return render(request, 'campaña_detalle_crear.html', {'form':form,'campaña':campaña})
		
@group_required(('Auditor Campañas', '/accounts/login/'))
def analisis(request, pk_campaña, pk_analisis):
	campaña =get_object_or_404(Campaña, pk=pk_campaña)
	analisis = get_object_or_404(Analisis, pk=pk_analisis)
	reportes = Reporte.objects.filter(fk_analisis=analisis)
	return render(request, 'analisis.html',{'reportes':reportes,
															'analisis':analisis,
															'campaña':campaña})

@group_required(('Auditor Funciones', '/accounts/login/'))
def funciones_borrar(request, pk):
	if request.method == 'POST':
		funcion = Funcion.objects.get(pk=pk)
		funcion.delete()
	return redirect('funciones_list')
	
def analisis_borrar(request, pk_campaña, pk_analisis):
	if request.method == 'POST':
		analisis = get_object_or_404(Analisis, pk=pk_analisis)
		analisis.delete()
	return redirect('campañas_detalle', pk_campaña)
	

@group_required(('Auditor Campañas', '/accounts/login/'))
def transcripcion(request, pk_campaña, pk_analisis, pk_reporte):
    reporte = Reporte.objects.get(pk=pk_reporte)
    campaña =get_object_or_404(Campaña, pk=pk_campaña)
    analisis = get_object_or_404(Analisis, pk=pk_analisis)
    palabras = Palabras.objects.filter(fk_funcion=reporte.fk_funcion)
    
    #Generar tabla con el texto trascripto
    contador = 0
    c1 = reporte.canal_1.split("|")
    c2 = reporte.canal_2.split("|")

    if len(c1) == len(c2):
        reporte = []
        for i in range(len(c1)):
            reporte.append([contador + "-" + str(contador+30),
                            c1[i],
                            c2[i]])
            contador += 30

    return render(request, 'transcripcion.html', {'reporte':reporte,
													'analisis':analisis,
													'campaña':campaña,
													'palabras':palabras})
	
	
	
def reproducir(request, pk_audio):
	original = "M:\\FreeLance\\Audios\\190810\\"
	pathTMP = "M:\\FreeLance\\Biometria\\static\\media\\audios\\tmp\\"
	audio = get_object_or_404(Audio,pk=pk_audio)
	filename = audio.file.path.split("\\")[-1]
	convertir = "M:\\FreeLance\\ffmpeg.exe   -acodec g729 -i " + original + filename + " -acodec pcm_s16le -y -f wav " + pathTMP + filename
	os.system(convertir)
	#return redirect('reproducir.html', audio.file.path)
	#return render(request,'reproducir.html',{'audio':audio})
	return HttpResponseRedirect('/media/audios/tmp/' + filename)
	
def cambiarEstado(request, pk_funcion):
	data = dict()
	funcion = Funcion.objects.get(id=pk_funcion)
	if funcion.estado == 1:
		funcion.estado = 2
		funcion.save()
		data['is_valid']=True
		data['html_funcion'] = render_to_string('includes/funcion_parcial_detalle.html',{'funcion':funcion},request)
	else:
		if funcion.ponderacion == 100:
			funcion.estado = 1
			funcion.save()
			data['is_valid']=True
			data['html_funcion'] = render_to_string('includes/funcion_parcial_detalle.html',{'funcion':funcion},request)
		else:
			data['is_valid']=False
		
	return JsonResponse(data)
	
	
	


def buscar(request):
	audios = Audio.objects.all()
	reporte_filter = ReporteFilter(request.GET, queryset=audios)
	return render(request, 'buscar.html',{'filter': reporte_filter})



@group_required(('Auditor Reportes', '/accounts/login/'))
def comentario_audio(request, pk_audio):
	data = dict()
	audio = get_object_or_404(Audio, pk=pk_audio)
	if request.method == 'POST':
		form = ComentarioAudioForm(request.POST, instance=audio)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
	else:
		form = ComentarioAudioForm(instance=audio)
	
	context = {'form':form,'audio':audio}
	data['html_form'] = render_to_string('includes/comentario_parcial.html',context,request)

	
	return JsonResponse(data)

@group_required(('Auditor Reportes', '/accounts/login/'))
def comentario_reporte(request, pk_reporte):
	data = dict()
	reporte = get_object_or_404(Reporte, pk=pk_reporte)
	if request.method == 'POST':
		form = ComentarioReporteForm(request.POST, instance=reporte)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
	else:
		form = ComentarioReporteForm(instance=reporte)
	
	context = {'form':form,'reporte':reporte}
	data['html_form'] = render_to_string('includes/comentarioReporte_parcial.html',context,request)

	
	return JsonResponse(data)


@group_required(('Auditor Graficos', '/accounts/login/'))
def graficos(request):
	return render(request, 'graficos.html')

@group_required(('Auditor Graficos', '/accounts/login/'))
def graficoCampañas(request):
	campañas = Campaña.objects.all()
	campañasNombre = []
	campañasPromedio = []
	for camp in campañas:
		campañasNombre.append(str(camp))
		campañasPromedio.append(random.randint(0,100))
	altura = len(campañasNombre) * 8
	return render(request, 'graficos/graficoCampañas.html',{'campañasNombre':campañasNombre[:20],'campañasPromedio':campañasPromedio[:20],'altura':altura})

@group_required(('Auditor Graficos', '/accounts/login/'))
def graficoAgentes(request):
	agentes = Agente.objects.all()
	agentesNombre = []
	agentesPromedio = []
	for agente in agentes:
		agentesNombre.append(str(agente))
		agentesPromedio.append(random.randint(0,100))
	altura = len(agentesNombre) * 12
	return render(request, 'graficos/graficoAgentes.html',
		{'agentesNombre':agentesNombre,
		'agentesPromedio':agentesPromedio,'altura':altura})

@group_required(('Auditor Graficos', '/accounts/login/'))
def graficoV1(request):
    context = {}
    if request.method == 'POST':
        camp = request.POST.get('campaña', 0)
        agente = request.POST.get('agente', 0)
        ponderacion = request.POST.get('ponderacion', 0)
        try:
            ponderacion = int(ponderacion)
        except:
            ponderacion = 0

        if agente != 0:
            if camp != 0 :
                if ponderacion != 0:
                    audios = Audio.objects.filter(agente=agente, campaña=camp, ponderacion__lt=ponderacion).order_by('ponderacion')
                else:
                    audios = Audio.objects.filter(agente=agente, campaña=camp).order_by('ponderacion')
                audioNombres = []
                audioPonderacion = []
                for a in audios:
                    audioNombres.append(a.idInteraccion)
                    audioPonderacion.append(a.ponderacion)
                context['labelsList'] = audioNombres
                context['dataList'] = audioPonderacion
                if len(audioNombres) * 24 < 300:
                    context['altura'] = 300
                else:
                    context['altura'] = len(audioNombres) * 24

                agenteNombre = Agente.objects.get(id=agente).nombre
                campañaNombre = Campaña.objects.get(id=camp).nombre
                context['texto'] = "'Audios de la campaña " + campañaNombre  + " del agente " + agenteNombre + "'"
            else:
                agente = Agente.objects.get(id=agente)
                audios = Audio.objects.filter(agente=agente)
                campañas = []
                for a in audios:
                    campañas.append(a.campaña.nombre)
                campañas = list(dict.fromkeys(campañas))
                data = []
                for c in campañas:
                    c = Campaña.objects.get(nombre=c)
                    audios = Audio.objects.filter(campaña=c)
                    count = 0
                    sum = 0
                    for a in audios:
                        count += 1
                        sum = sum + a.ponderacion
                    data.append(sum/count)
                if ponderacion != 0:
                    sacar = []
                    pos = 0
                    for d in data:
                        if d < int(ponderacion):
                            sacar.append(pos)
                        pos += 1
                    for s in sacar:
                        campañas.pop(s)
                        data.pop(s)

                context['labelsList'] = campañas
                context['dataList'] = data
                context['texto'] = "'Ponderacion promedio de las campañas del agente " + agente.nombre + "'"
                if len(campañas) * 24 < 300:
                    context['altura'] = 300
                else:
                    context['altura'] = len(campañas) * 24
        elif camp != 0:
            campañaNombre = Campaña.objects.get(id=camp).nombre
            audios = Audio.objects.filter(campaña=camp).order_by('ponderacion')
            agentes = []
            for a in audios:
                agentes.append(a.agente.nombre)
            agentes = list(dict.fromkeys(agentes))
            data = []
            for ag in agentes:
                ag = Agente.objects.get(nombre=ag)
                audios = Audio.objects.filter(agente=ag)
                count = 0
                sum = 0
                for a in audios:
                    count += 1
                    sum = sum + a.ponderacion
                data.append(sum/count)
            if ponderacion != 0:
                sacar = []
                pos = 0
                for d in data:
                    if d < int(ponderacion):
                        sacar.append(pos)
                    pos += 1
                for s in sacar:
                    agentes.pop(s)
                    data.pop(s)
            
            context['labelsList'] = agentes
            context['dataList'] = data
            context['texto'] = "'Ponderacion promedio de los agentes en la campaña " + campañaNombre + "'"
            if len(agentes) * 24 < 300:
                context['altura'] = 300
            else:
                context['altura'] = len(agentes) * 24

    
    context['agentes'] = Agente.objects.all().order_by('nombre')
    context['campañas'] = Campaña.objects.all().order_by('nombre')
    #altura = len(agentesNombre) * 12
    return render(request, 'graficos/grafico_V1.html',context)



@group_required(('Auditor Campañas', '/accounts/login/'))
def test(request, pk_campaña):
    camp = Campaña.objects.get(pk=pk_campaña)
    funciones = Funcion.objects.filter(estado=1)
    funciones = funciones.difference(camp.fk_funciones.all())
    return render(request, 'test.html',{'camp':camp,'funciones':funciones})