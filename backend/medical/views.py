from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from medical.services import AsistenteVirtualService
from medical.models import ConversacionIA

asistente_service = AsistenteVirtualService()


@csrf_exempt
@require_http_methods(["POST"])
def iniciar_conversacion(request):
    """
    Inicia una nueva conversación con el asistente virtual
    
    POST /api/asistente/iniciar/
    Body: {
        "paciente_id": 1,
        "titulo": "Consulta sobre dolor de cabeza" (opcional)
    }
    """
    try:
        data = json.loads(request.body)
        paciente_id = data.get('paciente_id')
        titulo = data.get('titulo', 'Nueva Consulta con Asistente')
        
        if not paciente_id:
            return JsonResponse({
                'exito': False,
                'error': 'El campo paciente_id es requerido'
            }, status=400)
        
        conversacion = asistente_service.iniciar_conversacion(paciente_id, titulo)
        
        # Mensaje de bienvenida
        mensaje_bienvenida = conversacion.mensajes.filter(rol='asistente').first()
        
        return JsonResponse({
            'exito': True,
            'conversacion_id': conversacion.id,
            'titulo': conversacion.titulo,
            'mensaje_bienvenida': mensaje_bienvenida.contenido if mensaje_bienvenida else None,
            'paciente': {
                'id': conversacion.paciente.id,
                'nombre': conversacion.paciente.nombre,
                'edad': conversacion.paciente.edad()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def enviar_mensaje(request):
    """
    Envía un mensaje del paciente y obtiene respuesta del asistente
    
    POST /api/asistente/mensaje/
    Body: {
        "conversacion_id": 1,
        "mensaje": "Me duele mucho la cabeza desde ayer"
    }
    """
    try:
        data = json.loads(request.body)
        conversacion_id = data.get('conversacion_id')
        mensaje = data.get('mensaje')
        
        if not conversacion_id or not mensaje:
            return JsonResponse({
                'exito': False,
                'error': 'Los campos conversacion_id y mensaje son requeridos'
            }, status=400)
        
        resultado = asistente_service.enviar_mensaje(conversacion_id, mensaje)
        
        return JsonResponse(resultado)
        
    except ConversacionIA.DoesNotExist:
        return JsonResponse({
            'exito': False,
            'error': 'Conversación no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def finalizar_conversacion(request):
    """
    Finaliza una conversación activa
    
    POST /api/asistente/finalizar/
    Body: {
        "conversacion_id": 1
    }
    """
    try:
        data = json.loads(request.body)
        conversacion_id = data.get('conversacion_id')
        
        if not conversacion_id:
            return JsonResponse({
                'exito': False,
                'error': 'El campo conversacion_id es requerido'
            }, status=400)
        
        resultado = asistente_service.finalizar_conversacion(conversacion_id)
        
        return JsonResponse(resultado)
        
    except ConversacionIA.DoesNotExist:
        return JsonResponse({
            'exito': False,
            'error': 'Conversación no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def obtener_historial(request, conversacion_id):
    """
    Obtiene el historial completo de una conversación
    
    GET /api/asistente/historial/<conversacion_id>/
    """
    try:
        resultado = asistente_service.obtener_historial(conversacion_id)
        return JsonResponse(resultado)
        
    except ConversacionIA.DoesNotExist:
        return JsonResponse({
            'exito': False,
            'error': 'Conversación no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def listar_conversaciones(request, paciente_id):
    """
    Lista todas las conversaciones de un paciente
    
    GET /api/asistente/conversaciones/<paciente_id>/
    """
    try:
        conversaciones = ConversacionIA.objects.filter(
            paciente_id=paciente_id
        ).order_by('-fecha_inicio')
        
        lista = []
        for conv in conversaciones:
            lista.append({
                'id': conv.id,
                'titulo': conv.titulo,
                'fecha_inicio': conv.fecha_inicio.isoformat(),
                'activa': conv.activa,
                'requiere_atencion': conv.requiere_atencion_medica,
                'nivel_urgencia': conv.nivel_urgencia,
                'sintomas': conv.sintomas_mencionados,
                'total_mensajes': conv.mensajes.count()
            })
        
        return JsonResponse({
            'exito': True,
            'conversaciones': lista
        })
        
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)

