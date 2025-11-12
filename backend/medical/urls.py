"""
URLs para el módulo medical - API REST
"""

from django.urls import path
from medical.views_api import (
    # Asistente Virtual
    AsistenteIniciarView,
    AsistenteMensajeView,
    AsistenteHistorialView,
    AsistenteFinalizarView,
    # Médicos
    MedicoListView,
    MedicoDetailView,
    MedicoHorariosView,
    # Citas
    CitaListView,
    CitaCreateView,
    CitaDetailView,
    CitaPDFView,
    CitaCancelarView,
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
]

