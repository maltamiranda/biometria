
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
    path('ajax/editar_palabra/<int:pk_funcion>/<int:pk_palabra>', views.editar_palabra, name='editar_palabra'),
    path('ajax/borrar_palabra/<int:pk_funcion>/<int:pk_palabra>', views.borrar_palabra, name='borrar_palabra'),
    #path('audios/analizar/<int:pk>/', views.analizar, name='analizar'),
    #path('test/', views.test, name='test'),
    #path('audios/', views.audio_list, name='audio_list'),
    #path('audios/upload/', views.upload_audio, name='upload_audio'),
    #path('audios/<int:pk>/', views.delete_audio, name='delete_audio'),
    path('reportes/<int:pk>/', views.reporte_generado, name='reporte_generado'),
    path('reportes/', views.reportes, name='reportes'),
    #path('singup/', views.singup, name='singup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ajax/cargar_funcion_descripcion/', views.cargar_funcion_descripcion, name='cargar_funcion_descripcion'),
    path('campañas/', views.campañas, name='campañas'),
    path('campañas/<int:pk_campaña>/', views.campañas_detalle, name='campañas_detalle'),
    path('campañas/<int:pk_campaña>/crear', views.capañas_detalle_crear, name='capañas_detalle_crear'),
    path('campañas/<int:pk_campaña>/<int:pk_campaña_funcion>/', views.campaña_funcion_analisis, name='campaña_funcion_analisis'),
    path('campañas/<int:pk_campaña>/<int:pk_campaña_funcion>/<int:pk_audio>/', views.transcripcion, name='transcripcion'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)