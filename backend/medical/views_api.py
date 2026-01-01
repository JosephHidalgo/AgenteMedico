"""
Views API REST para el sistema médico
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from datetime import datetime, date

from .models import Paciente, Medico, Cita, HorarioMedico
from .serializers import (
    PacienteListSerializer,
    MedicoSerializer,
    CitaListSerializer,
    CitaDetailSerializer,
    CitaCreateSerializer,
    MensajeAsistenteSerializer
)
from .services.asistente_virtual_redis import AsistenteVirtualService
from .services.cita_service import CitaService
from .services.pdf_service import PDFService


# ====================
# ASISTENTE VIRTUAL
# ====================

class AsistenteIniciarView(APIView):
    """
    POST /api/asistente/iniciar/
    Inicia una nueva conversación con el asistente virtual
    """
    
    def post(self, request):
        asistente = AsistenteVirtualService()
        resultado = asistente.iniciar_conversacion()
        
        return Response({
            'exito': True,
            'conversacion_id': resultado['conversacion_id'],
            'mensaje': resultado['mensaje_inicial']
        }, status=status.HTTP_201_CREATED)


class AsistenteMensajeView(APIView):
    """
    POST /api/asistente/mensaje/
    Envía un mensaje al asistente y obtiene respuesta
    
    Body:
        {
            "conversacion_id": "uuid",
            "mensaje": "string"
        }
    """
    
    def post(self, request):
        serializer = MensajeAsistenteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'exito': False,
                'errores': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        conversacion_id = serializer.validated_data.get('conversacion_id')
        mensaje = serializer.validated_data['mensaje']
        
        asistente = AsistenteVirtualService()
        
        # Si no hay conversacion_id, iniciar una nueva
        if not conversacion_id:
            resultado_inicio = asistente.iniciar_conversacion()
            conversacion_id = resultado_inicio['conversacion_id']
        
        resultado = asistente.enviar_mensaje(conversacion_id, mensaje)
        
        return Response({
            'exito': True,
            'conversacion_id': conversacion_id if not resultado.get('nueva_conversacion') else resultado.get('conversacion_id'),
            'respuesta': resultado['respuesta'],
            'intencion': resultado.get('intencion'),
            'requiere_datos': resultado.get('requiere_datos', False),
            'especialidad_sugerida': resultado.get('especialidad_sugerida'),
            'es_urgente': resultado.get('es_urgente', False)
        }, status=status.HTTP_200_OK)


class AsistenteHistorialView(APIView):
    """
    GET /api/asistente/historial/{conversacion_id}/
    Obtiene el historial de una conversación
    """
    
    def get(self, request, conversacion_id):
        asistente = AsistenteVirtualService()
        historial = asistente.obtener_historial(conversacion_id)
        
        if not historial:
            return Response({
                'exito': False,
                'error': 'Conversación no encontrada o expirada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'exito': True,
            'conversacion_id': conversacion_id,
            'mensajes': historial
        }, status=status.HTTP_200_OK)


class AsistenteFinalizarView(APIView):
    """
    DELETE /api/asistente/finalizar/{conversacion_id}/
    Finaliza una conversación
    """
    
    def delete(self, request, conversacion_id):
        asistente = AsistenteVirtualService()
        eliminado = asistente.finalizar_conversacion(conversacion_id)
        
        return Response({
            'exito': True,
            'mensaje': 'Conversación finalizada'
        }, status=status.HTTP_200_OK)


class AsistenteCrearCitaView(APIView):
    """
    POST /api/asistente/crear-cita/
    Crea una cita basándose en la conversación del asistente
    
    Body:
        {
            "conversacion_id": "uuid"
        }
    """
    
    def post(self, request):
        conversacion_id = request.data.get('conversacion_id')
        
        print(f"[DEBUG] Recibido conversacion_id: {conversacion_id}")
        print(f"[DEBUG] Request data: {request.data}")
        
        if not conversacion_id:
            return Response({
                'exito': False,
                'error': 'Se requiere conversacion_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        asistente = AsistenteVirtualService()
        resultado = asistente.crear_cita_desde_conversacion(conversacion_id)
        
        print(f"[DEBUG] Resultado: {resultado}")
        
        if resultado['exito']:
            return Response(resultado, status=status.HTTP_201_CREATED)
        else:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)


# ====================
# PACIENTES
# ====================

class PacienteListView(APIView):
    """
    GET /api/pacientes/
    Lista todos los pacientes que han sacado citas.
    Los datos sensibles (teléfono, email) se devuelven parcialmente ocultos.
    Incluye las especialidades médicas en las que cada paciente ha tenido citas.
    
    Filtros opcionales: 
        ?activo=true/false
        ?buscar=nombre
    """
    
    def get(self, request):
        # Solo pacientes que tienen al menos una cita
        pacientes = Paciente.objects.filter(
            citas__isnull=False
        ).distinct().prefetch_related('citas__medico')
        
        # Filtrar por estado activo
        activo = request.query_params.get('activo')
        if activo is not None:
            pacientes = pacientes.filter(activo=activo.lower() == 'true')
        
        # Filtrar por nombre
        buscar = request.query_params.get('buscar')
        if buscar:
            from django.db.models import Q
            pacientes = pacientes.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido_paterno__icontains=buscar) |
                Q(apellido_materno__icontains=buscar)
            )
        
        serializer = PacienteListSerializer(pacientes, many=True)
        
        return Response({
            'exito': True,
            'cantidad': pacientes.count(),
            'pacientes': serializer.data
        }, status=status.HTTP_200_OK)


# ====================
# MÉDICOS
# ====================

class MedicoListView(APIView):
    """
    GET /api/medicos/
    Lista todos los médicos disponibles
    Filtros opcionales: ?especialidad=Cardiología
    """
    
    def get(self, request):
        medicos = Medico.objects.filter(activo=True)
        
        # Filtrar por especialidad si se proporciona
        especialidad = request.query_params.get('especialidad')
        if especialidad:
            medicos = medicos.filter(especialidad__icontains=especialidad)
        
        serializer = MedicoSerializer(medicos, many=True)
        
        return Response({
            'exito': True,
            'cantidad': medicos.count(),
            'medicos': serializer.data
        }, status=status.HTTP_200_OK)


class MedicoDetailView(APIView):
    """
    GET /api/medicos/{id}/
    Obtiene detalles de un médico específico
    """
    
    def get(self, request, pk):
        medico = get_object_or_404(Medico, pk=pk, activo=True)
        serializer = MedicoSerializer(medico)
        
        return Response({
            'exito': True,
            'medico': serializer.data
        }, status=status.HTTP_200_OK)


class MedicoHorariosView(APIView):
    """
    GET /api/medicos/{id}/horarios/
    Obtiene horarios disponibles de un médico
    Query params opcionales:
        ?fecha=2025-11-06
        ?cantidad=5
    """
    
    def get(self, request, pk):
        medico = get_object_or_404(Medico, pk=pk, activo=True)
        
        fecha_param = request.query_params.get('fecha')
        cantidad = int(request.query_params.get('cantidad', 10))
        
        if fecha_param:
            try:
                fecha = datetime.strptime(fecha_param, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'exito': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            fecha = date.today()
        
        # Obtener horarios alternativos disponibles
        horarios = CitaService.obtener_horarios_alternativos(
            medico.id,
            fecha,
            cantidad=cantidad
        )
        
        return Response({
            'exito': True,
            'medico': {
                'id': medico.id,
                'nombre': medico.nombre_completo(),
                'especialidad': medico.especialidad
            },
            'horarios_disponibles': horarios
        }, status=status.HTTP_200_OK)


# ====================
# CITAS
# ====================

class CitaListView(APIView):
    """
    GET /api/citas/
    Lista todas las citas
    Filtros opcionales:
        ?estado=AGENDADA
        ?medico=1
        ?fecha=2025-11-06
    
    POST /api/citas/
    Crea una nueva cita médica
    """
    
    def get(self, request):
        citas = Cita.objects.all().select_related('paciente', 'medico')
        
        # Filtros
        estado = request.query_params.get('estado')
        if estado:
            citas = citas.filter(estado=estado)
        
        medico_id = request.query_params.get('medico')
        if medico_id:
            citas = citas.filter(medico_id=medico_id)
        
        # Filtro de fecha específica
        fecha_param = request.query_params.get('fecha')
        if fecha_param:
            try:
                fecha = datetime.strptime(fecha_param, '%Y-%m-%d').date()
                citas = citas.filter(fecha=fecha)
            except ValueError:
                pass
        
        # Filtro de rango de fechas
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            try:
                fecha_d = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                citas = citas.filter(fecha__gte=fecha_d)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_h = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                citas = citas.filter(fecha__lte=fecha_h)
            except ValueError:
                pass
        
        citas = citas.order_by('-fecha', '-hora')
        
        serializer = CitaListSerializer(citas, many=True)
        
        return Response({
            'exito': True,
            'cantidad': citas.count(),
            'citas': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Crear nueva cita"""
        serializer = CitaCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'exito': False,
                'errores': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        datos_validados = serializer.validated_data
        
        # Separar datos del paciente y de la cita
        datos_paciente = {
            'nombre': datos_validados['paciente_nombre'],
            'apellido_paterno': datos_validados['paciente_apellido_paterno'],
            'apellido_materno': datos_validados['paciente_apellido_materno'],
            'fecha_nacimiento': datos_validados['paciente_fecha_nacimiento'],
            'sexo': datos_validados['paciente_sexo'],
            'email': datos_validados['paciente_email'],
            'telefono': datos_validados['paciente_telefono']
        }
        
        datos_cita = {
            'medico_id': datos_validados['medico'].id,
            'fecha': datos_validados['fecha'],
            'hora': datos_validados['hora'],
            'motivo': datos_validados['motivo'],
            'sintomas_iniciales': datos_validados.get('sintomas_iniciales', '')
        }
        
        try:
            cita, creado, mensaje_servicio = CitaService.crear_cita(datos_paciente, datos_cita)
            serializer_respuesta = CitaDetailSerializer(cita)
            
            return Response({
                'exito': True,
                'mensaje': mensaje_servicio,
                'cita': serializer_respuesta.data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({
                'exito': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CitaCreateView(APIView):
    """
    POST /api/citas/
    Crea una nueva cita médica
    
    Body:
        {
            "paciente_nombre": "Juan",
            "paciente_apellido": "Pérez",
            "paciente_edad": 30,
            "paciente_email": "juan@example.com",
            "paciente_telefono": "555-1234",
            "medico_id": 1,
            "fecha": "2025-11-10",
            "hora": "14:00",
            "motivo": "Consulta general",
            "sintomas_iniciales": "Dolor de cabeza"
        }
    """
    
    def post(self, request):
        serializer = CitaCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'exito': False,
                'errores': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        datos_validados = serializer.validated_data
        
        # Separar datos del paciente y de la cita
        datos_paciente = {
            'nombre': datos_validados['paciente_nombre'],
            'apellido': datos_validados['paciente_apellido'],
            'edad': datos_validados['paciente_edad'],
            'email': datos_validados['paciente_email'],
            'telefono': datos_validados['paciente_telefono']
        }
        
        datos_cita = {
            'medico_id': datos_validados['medico_id'],
            'fecha': datos_validados['fecha'],
            'hora': datos_validados['hora'],
            'motivo': datos_validados['motivo'],
            'sintomas_iniciales': datos_validados.get('sintomas_iniciales', '')
        }
        
        try:
            cita, creada, mensaje = CitaService.crear_cita(datos_paciente, datos_cita)
            serializer_respuesta = CitaDetailSerializer(cita)
            
            return Response({
                'exito': True,
                'mensaje': mensaje,
                'cita': serializer_respuesta.data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({
                'exito': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'exito': False,
                'error': f'Error al crear la cita: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CitaDetailView(APIView):
    """
    GET /api/citas/{id}/
    Obtiene detalles de una cita específica
    """
    
    def get(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)
        serializer = CitaDetailSerializer(cita)
        
        return Response({
            'exito': True,
            'cita': serializer.data
        }, status=status.HTTP_200_OK)


class CitaPDFView(APIView):
    """
    GET /api/citas/{id}/pdf/
    Genera y descarga el PDF de una cita
    """
    
    def get(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)
        
        try:
            # Generar PDF
            pdf_buffer = PDFService.generar_pdf_cita(cita)
            nombre_archivo = PDFService.obtener_nombre_archivo(cita)
            
            # Crear respuesta HTTP con el PDF
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            return Response({
                'exito': False,
                'error': f'Error al generar PDF: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CitaCancelarView(APIView):
    """
    POST /api/citas/{id}/cancelar/
    Cancela una cita
    
    Body:
        {
            "motivo": "No puedo asistir"
        }
    """
    
    def post(self, request, pk):
        motivo = request.data.get('motivo', '')
        
        exito, mensaje = CitaService.cancelar_cita(pk, motivo)
        
        if exito:
            return Response({
                'exito': True,
                'mensaje': mensaje
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'exito': False,
                'error': mensaje
            }, status=status.HTTP_400_BAD_REQUEST)


# ====================
# ESTADÍSTICAS
# ====================

class EstadisticasView(APIView):
    """
    GET /api/estadisticas/
    Retorna estadísticas generales del sistema optimizadas para dashboard
    
    Response:
        {
            "exito": true,
            "citas_hoy": 5,
            "citas_semana": 18,
            "total_pacientes": 247,
            "doctores_activos": 12
        }
    """
    
    def get(self, request):
        from datetime import timedelta
        from .models import Paciente
        
        hoy = date.today()
        fin_semana = hoy + timedelta(days=7)
        
        # Contar citas de hoy
        citas_hoy = Cita.objects.filter(
            fecha=hoy,
            estado='AGENDADA'
        ).count()
        
        # Contar citas de la semana
        citas_semana = Cita.objects.filter(
            fecha__gte=hoy,
            fecha__lt=fin_semana,
            estado='AGENDADA'
        ).count()
        
        # Total de pacientes activos
        total_pacientes = Paciente.objects.filter(activo=True).count()
        
        # Doctores activos
        doctores_activos = Medico.objects.filter(activo=True).count()
        
        return Response({
            'exito': True,
            'citas_hoy': citas_hoy,
            'citas_semana': citas_semana,
            'total_pacientes': total_pacientes,
            'doctores_activos': doctores_activos
        }, status=status.HTTP_200_OK)

