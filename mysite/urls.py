from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from mysite.core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('funciones/', views.funciones, name='funciones'),
    path('funciones_list/new', views.funciones_crear, name='funciones_crear'),
    path('funciones_list/', views.funciones_list, name='funciones_list'),
    path('funciones_list/<int:pk>', views.funciones_detalle, name='funciones_detalle'),
    path('funciones_list/<int:pk>/borrar', views.funciones_borrar, name='funciones_borrar'),
    path('ajax/crear_palabra/<int:pk_funcion>/', views.crear_palabra, name='crear_palabra'),
    path('ajax/comentario_audio/<int:pk_audio>', views.comentario_audio, name='comentario_audio'),
    path('ajax/comentario_reporte/<int:pk_reporte>', views.comentario_reporte, name='comentario_reporte'),
    path('ajax/editar_palabra/<int:pk_funcion>/<int:pk_palabra>', views.editar_palabra, name='editar_palabra'),
    path('ajax/borrar_palabra/<int:pk_funcion>/<int:pk_palabra>', views.borrar_palabra, name='borrar_palabra'),
    path('ajax/reportes/detalleAnalisis/<str:audio>', views.detalleAnalisis, name='detalleAnalisis'),
	path('ajax/cambiarEstado/<int:pk_funcion>', views.cambiarEstado, name='cambiarEstado'),
    path('ajax/cargar_funcion_descripcion/', views.cargar_funcion_descripcion, name='cargar_funcion_descripcion'),
    path('ajax/configCampañaFunciones/<int:pk_campaña>', views.configCampañaFunciones, name='configCampañaFunciones'),
    path('ajax/borrar_funcion/<int:pk_funcion>', views.borrar_funcion, name='borrar_funcion'),
    path('ajax/analizarAudio/<int:pk_audio>', views.analizarAudio, name='analizarAudio'),
    #path('audios/analizar/<int:pk>/', views.analizar, name='analizar'),
    #path('test/', views.test, name='test'),
    #path('audios/', views.audio_list, name='audio_list'),
    #path('audios/upload/', views.upload_audio, name='upload_audio'),
    #path('audios/<int:pk>/', views.delete_audio, name='delete_audio'),
    path('reportes/<int:pk_reporte>/', views.reporte_generado, name='reporte_generado'),
    #path('reportes/', views.buscar, name='buscar'),
    path('reportes/', views.reportes, name='reportes'),
	path('reportes/play/<int:pk_audio>/', views.reproducir, name='reproducir'),
    #path('singup/', views.singup, name='singup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('campañas/', views.campañas, name='campañas'),
    path('campañas/<int:pk_campaña>/', views.campañas_detalle, name='campañas_detalle'),
    path('campañas/<int:pk_campaña>/crear', views.capañas_detalle_crear, name='capañas_detalle_crear'),
    path('campañas/<int:pk_campaña>/<int:pk_analisis>/', views.analisis, name='analisis'),
    path('campañas/<int:pk_campaña>/<int:pk_analisis>/borrar', views.analisis_borrar, name='analisis_borrar'),
    path('campañas/<int:pk_campaña>/<int:pk_analisis>/<int:pk_reporte>/', views.transcripcion, name='transcripcion'),
    url(r'^buscar/$', views.buscar, name='buscar'),
    path('reproducir/<str:audio>', views.reproducir, name='reproducir'),
    path('graficos', views.graficoV1, name='graficoV1'),
    path('graficos/campañas', views.graficoCampañas, name='graficoCampañas'),
    path('graficos/agentes', views.graficoAgentes, name='graficoAgentes'),
    #path('graficos/v1', views.graficoV1, name='graficoV1'),
    #path('test', views.graficoV1, name='graficoV1'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)