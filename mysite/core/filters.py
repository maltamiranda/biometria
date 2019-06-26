from .models import Reporte
import django_filters

class ReporteFilter(django_filters.FilterSet):
	#ponderacion__gt = django_filters.NumberFilter(field_name='ponderacion', lookup_expr='gt')
	#ponderacion__lt = django_filters.NumberFilter(field_name='ponderacion', lookup_expr='lt')
	class Meta:
		model = Reporte
		fields = {'ponderacion': ['lt', 'gt'],
					'nombre_agente':['icontains'],
					'nombre_audio':['icontains'],
					'nombre_campaña':['icontains']}
		#fields = ['ponderacion','nombre_agente','nombre_audio','nombre_campaña']