
from django.contrib import admin
from django.urls import path, include
from mysite.core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('funciones/', views.funciones, name='funciones'),
    path('audios/analizar/<int:pk>/', views.analizar, name='analizar'),
    path('test/', views.test, name='test'),
    path('audios/', views.audio_list, name='audio_list'),
    path('audios/upload/', views.upload_audio, name='upload_audio'),
    path('audios/<int:pk>/', views.delete_audio, name='delete_audio'),
    path('reportes/<int:pk>/', views.reporte_generado, name='reporte_generado'),
    path('reportes/', views.reportes, name='reportes'),
    path('singup/', views.singup, name='singup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ajax/cargar_funcion_descripcion/', views.cargar_funcion_descripcion, name='cargar_funcion_descripcion'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)