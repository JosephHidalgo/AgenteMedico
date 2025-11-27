"""
URLs para el módulo medical - API REST
"""

from django.urls import path
from medical.views_api import (
    AsistenteIniciarView,
    AsistenteMensajeView,
    AsistenteHistorialView,
    AsistenteFinalizarView,
    AsistenteCrearCitaView,
    PacienteListView,
    MedicoListView,
    MedicoDetailView,
    MedicoHorariosView,
    CitaListView,
    CitaCreateView,
    CitaDetailView,
    CitaPDFView,
    CitaCancelarView,
    EstadisticasView,
)

app_name = 'medical'

urlpatterns = [
    # ======================
    # ASISTENTE VIRTUAL
    # ======================
    path('api/asistente/iniciar/', AsistenteIniciarView.as_view(), name='asistente_iniciar'),
    path('api/asistente/mensaje/', AsistenteMensajeView.as_view(), name='asistente_mensaje'),
    path('api/asistente/historial/<str:conversacion_id>/', AsistenteHistorialView.as_view(), name='asistente_historial'),
    path('api/asistente/finalizar/<str:conversacion_id>/', AsistenteFinalizarView.as_view(), name='asistente_finalizar'),
    path('api/asistente/crear-cita/', AsistenteCrearCitaView.as_view(), name='asistente_crear_cita'),
    
    # ======================
    # PACIENTES
    # ======================
    path('api/pacientes/', PacienteListView.as_view(), name='paciente_list'),
    
    # ======================
    # MÉDICOS
    # ======================
    path('api/medicos/', MedicoListView.as_view(), name='medico_list'),
    path('api/medicos/<int:pk>/', MedicoDetailView.as_view(), name='medico_detail'),
    path('api/medicos/<int:pk>/horarios/', MedicoHorariosView.as_view(), name='medico_horarios'),
    
    # ======================
    # CITAS
    # ======================
    path('api/citas/', CitaListView.as_view(), name='cita_list'),
    path('api/citas/<int:pk>/', CitaDetailView.as_view(), name='cita_detail'),
    path('api/citas/<int:pk>/pdf/', CitaPDFView.as_view(), name='cita_pdf'),
    path('api/citas/<int:pk>/cancelar/', CitaCancelarView.as_view(), name='cita_cancelar'),
    
    # ======================
    # ESTADÍSTICAS
    # ======================
    path('api/estadisticas/', EstadisticasView.as_view(), name='estadisticas'),
]

