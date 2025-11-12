"""
Servicio de Asistente Virtual con OpenAI ChatGPT y Redis
Este módulo maneja todas las interacciones con la API de OpenAI usando Redis para cache
"""

from openai import OpenAI
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import uuid
import json
import re


class AsistenteVirtualService:
    """
    Servicio para manejar conversaciones con el asistente virtual de IA
    Usa Redis para almacenar temporalmente las conversaciones (30 minutos)
    """
    
    def __init__(self):
        """Inicializa el cliente de OpenAI"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.modelo = settings.OPENAI_MODEL
        self.timeout = settings.ASISTENTE_CONFIG.get('timeout_conversacion', 1800)  # 30 min
        self.max_mensajes = settings.ASISTENTE_CONFIG.get('max_historial_mensajes', 20)
    
    def _get_cache_key(self, conversacion_id):
        """Genera la clave de cache para una conversación"""
        return f"conversacion:{conversacion_id}"
    
    def _get_system_prompt(self):
        """
        Define el comportamiento y personalidad del asistente médico virtual
        MODIFICADO para sistema de portfolio - Proactivo y guiado
        """
        return """Eres un asistente médico virtual amigable y profesional para un sistema de demostración.

Tu función principal es:

1. **SALUDO INICIAL**: Cuando un usuario inicie la conversación, salúdalo calurosamente y ofrécele DOS opciones claras:
   - "Evaluar síntomas que tengas"
   - "Agendar una cita médica"

2. **SI EL USUARIO MENCIONA SÍNTOMAS**:
   - Haz 2-3 preguntas de seguimiento relevantes
   - Evalúa la gravedad
   - Recomienda la especialidad médica apropiada
   - Pregunta: "¿Deseas agendar una cita con [Especialidad]?"

3. **SI EL USUARIO QUIERE AGENDAR CITA**:
   - Si vino de evaluación de síntomas, sugiere la especialidad apropiada
   - Si es directo, pregunta: "¿Qué especialidad médica necesitas?"
   - Una vez definida la especialidad, SOLICITA sus datos personales:
     * Nombre completo
     * Edad
     * Email
     * Teléfono
   - Confirma los datos antes de proceder

4. **DETECCIÓN DE INTENCIÓN**:
   - Identifica si el usuario quiere: [SINTOMAS] o [AGENDAR_CITA]
   - Marca claramente la intención en tu respuesta

5. **SÉ CONCISO Y DIRECTO**:
   - Respuestas claras y breves
   - Usa emojis moderadamente
   - Guía al usuario paso a paso

6. **IMPORTANTE**:
   - NO diagnostiques
   - Si detectas síntomas graves, recomienda atención inmediata
   - Sé empático pero profesional

**SÍNTOMAS DE ALARMA** (requieren atención urgente):
- Dolor de pecho intenso
- Dificultad severa para respirar
- Sangrado abundante
- Alteración de conciencia
- Fiebre >40°C persistente

**ESPECIALIDADES DISPONIBLES**:
- Medicina General
- Cardiología
- Endocrinología
- Dermatología
- Pediatría
- Traumatología
- Psicología

Responde siempre en español y de forma amigable."""
    
    def iniciar_conversacion(self):
        """
        Inicia una nueva conversación y retorna el ID
        
        Returns:
            dict: {
                'conversacion_id': str (UUID),
                'mensaje_inicial': str
            }
        """
        conversacion_id = str(uuid.uuid4())
        
        # Mensaje inicial del asistente
        mensaje_inicial = """¡Hola! 👋 Soy tu asistente médico virtual.

¿En qué puedo ayudarte hoy?

🩺 **Evaluar síntomas**
📅 **Agendar una cita médica**

Por favor, cuéntame en qué puedo asistirte."""
        
        # Crear estructura de conversación en Redis
        conversacion_data = {
            'conversacion_id': conversacion_id,
            'inicio': timezone.now().isoformat(),
            'mensajes': [
                {
                    'role': 'system',
                    'content': self._get_system_prompt()
                },
                {
                    'role': 'assistant',
                    'content': mensaje_inicial
                }
            ],
            'intencion': None,  # 'sintomas' o 'agendar_cita'
            'datos_paciente': None,  # Se llena cuando se soliciten datos
            'especialidad_sugerida': None
        }
        
        # Guardar en Redis con timeout de 30 minutos
        cache_key = self._get_cache_key(conversacion_id)
        cache.set(cache_key, json.dumps(conversacion_data), self.timeout)
        
        return {
            'conversacion_id': conversacion_id,
            'mensaje_inicial': mensaje_inicial
        }
    
    def obtener_conversacion(self, conversacion_id):
        """
        Obtiene una conversación existente desde Redis
        
        Args:
            conversacion_id (str): UUID de la conversación
        
        Returns:
            dict or None: Datos de la conversación o None si no existe/expiró
        """
        cache_key = self._get_cache_key(conversacion_id)
        data = cache.get(cache_key)
        
        if data:
            return json.loads(data)
        return None
    
    def guardar_conversacion(self, conversacion_data):
        """
        Guarda/actualiza una conversación en Redis
        
        Args:
            conversacion_data (dict): Datos de la conversación
        """
        cache_key = self._get_cache_key(conversacion_data['conversacion_id'])
        cache.set(cache_key, json.dumps(conversacion_data), self.timeout)
    
    def enviar_mensaje(self, conversacion_id, mensaje_usuario):
        """
        Envía un mensaje del usuario y obtiene respuesta del asistente
        
        Args:
            conversacion_id (str): UUID de la conversación
            mensaje_usuario (str): Mensaje del usuario
        
        Returns:
            dict: {
                'respuesta': str,
                'intencion': str or None,
                'requiere_datos': bool,
                'especialidad_sugerida': str or None,
                'es_urgente': bool
            }
        """
        # Obtener conversación
        conversacion = self.obtener_conversacion(conversacion_id)
        
        if not conversacion:
            # Conversación expirada o no existe - crear nueva
            resultado = self.iniciar_conversacion()
            return {
                'respuesta': resultado['mensaje_inicial'],
                'intencion': None,
                'requiere_datos': False,
                'especialidad_sugerida': None,
                'es_urgente': False,
                'nueva_conversacion': True,
                'conversacion_id': resultado['conversacion_id']
            }
        
        # Agregar mensaje del usuario al historial
        conversacion['mensajes'].append({
            'role': 'user',
            'content': mensaje_usuario
        })
        
        # Limitar historial
        mensajes_sistema = [m for m in conversacion['mensajes'] if m['role'] == 'system']
        mensajes_conversacion = [m for m in conversacion['mensajes'] if m['role'] != 'system']
        
        if len(mensajes_conversacion) > self.max_mensajes:
            mensajes_conversacion = mensajes_conversacion[-self.max_mensajes:]
        
        mensajes_para_api = mensajes_sistema + mensajes_conversacion
        
        # Llamar a OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=mensajes_para_api,
                max_tokens=settings.ASISTENTE_CONFIG.get('max_tokens', 800),
                temperature=settings.ASISTENTE_CONFIG.get('temperature', 0.7)
            )
            
            respuesta_asistente = response.choices[0].message.content
            
            # Agregar respuesta al historial
            conversacion['mensajes'].append({
                'role': 'assistant',
                'content': respuesta_asistente
            })
            
            # Analizar intención y contenido
            analisis = self._analizar_respuesta(mensaje_usuario, respuesta_asistente, conversacion)
            
            # Actualizar conversación
            if analisis['intencion']:
                conversacion['intencion'] = analisis['intencion']
            
            if analisis['especialidad_sugerida']:
                conversacion['especialidad_sugerida'] = analisis['especialidad_sugerida']
            
            # Guardar conversación actualizada
            self.guardar_conversacion(conversacion)
            
            return {
                'respuesta': respuesta_asistente,
                'intencion': conversacion.get('intencion'),
                'requiere_datos': analisis['requiere_datos'],
                'especialidad_sugerida': conversacion.get('especialidad_sugerida'),
                'es_urgente': analisis['es_urgente'],
                'nueva_conversacion': False
            }
            
        except Exception as e:
            # Error en la API de OpenAI
            return {
                'respuesta': f"Lo siento, hubo un error al procesar tu mensaje: {str(e)}",
                'intencion': None,
                'requiere_datos': False,
                'especialidad_sugerida': None,
                'es_urgente': False,
                'error': True
            }
    
    def _analizar_respuesta(self, mensaje_usuario, respuesta_asistente, conversacion):
        """
        Analiza el mensaje y la respuesta para detectar intención, urgencia y necesidad de datos
        
        Returns:
            dict: Análisis de la conversación
        """
        mensaje_lower = mensaje_usuario.lower()
        respuesta_lower = respuesta_asistente.lower()
        
        # Detectar intención
        intencion = conversacion.get('intencion')
        
        if not intencion:
            # Detectar palabras clave de síntomas
            sintomas_keywords = [
                'dolor', 'duele', 'siento', 'tengo', 'fiebre', 'tos', 'mareo',
                'náusea', 'vómito', 'malestar', 'cansancio', 'síntoma'
            ]
            
            # Detectar palabras clave de agendamiento
            cita_keywords = [
                'cita', 'agendar', 'turno', 'consulta', 'hora', 'reservar',
                'médico', 'doctor', 'especialista'
            ]
            
            sintomas_count = sum(1 for keyword in sintomas_keywords if keyword in mensaje_lower)
            cita_count = sum(1 for keyword in cita_keywords if keyword in mensaje_lower)
            
            if sintomas_count > cita_count:
                intencion = 'sintomas'
            elif cita_count > 0:
                intencion = 'agendar_cita'
        
        # Detectar si requiere datos del paciente
        requiere_datos = any(keyword in respuesta_lower for keyword in [
            'nombre', 'edad', 'email', 'teléfono', 'correo', 'datos'
        ])
        
        # Detectar especialidad sugerida
        especialidad_sugerida = None
        especialidades = {
            'medicina general': 'Medicina General',
            'cardiología': 'Cardiología',
            'cardiologia': 'Cardiología',
            'endocrinología': 'Endocrinología',
            'endocrinologia': 'Endocrinología',
            'dermatología': 'Dermatología',
            'dermatologia': 'Dermatología',
            'pediatría': 'Pediatría',
            'pediatria': 'Pediatría',
            'traumatología': 'Traumatología',
            'traumatologia': 'Traumatología',
            'psicología': 'Psicología',
            'psicologia': 'Psicología'
        }
        
        for key, value in especialidades.items():
            if key in respuesta_lower:
                especialidad_sugerida = value
                break
        
        # Detectar urgencia
        urgencia_keywords = [
            'urgente', 'inmediato', 'emergencia', 'grave', 'severo',
            'hospital', 'ambulancia', 'atención inmediata'
        ]
        
        es_urgente = any(keyword in respuesta_lower for keyword in urgencia_keywords)
        
        return {
            'intencion': intencion,
            'requiere_datos': requiere_datos,
            'especialidad_sugerida': especialidad_sugerida,
            'es_urgente': es_urgente
        }
    
    def obtener_historial(self, conversacion_id):
        """
        Obtiene el historial de mensajes de una conversación
        
        Args:
            conversacion_id (str): UUID de la conversación
        
        Returns:
            list: Lista de mensajes (sin el system prompt)
        """
        conversacion = self.obtener_conversacion(conversacion_id)
        
        if not conversacion:
            return []
        
        # Filtrar mensajes (excluir system prompt)
        mensajes = [
            m for m in conversacion['mensajes']
            if m['role'] != 'system'
        ]
        
        return mensajes
    
    def finalizar_conversacion(self, conversacion_id):
        """
        Finaliza y elimina una conversación de Redis
        
        Args:
            conversacion_id (str): UUID de la conversación
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        cache_key = self._get_cache_key(conversacion_id)
        cache.delete(cache_key)
        return True
