"""
Servicio de Asistente Virtual con OpenAI ChatGPT
Este módulo maneja todas las interacciones con la API de OpenAI
"""

from openai import OpenAI
from django.conf import settings
from medical.models import ConversacionIA, MensajeIA, Paciente
from django.utils import timezone
import re


class AsistenteVirtualService:
    """Servicio para manejar conversaciones con el asistente virtual de IA"""
    
    def __init__(self):
        """Inicializa el cliente de OpenAI"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.modelo = settings.OPENAI_MODEL
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self):
        """
        Define el comportamiento y personalidad del asistente médico virtual
        """
        return """Eres un asistente médico virtual profesional y empático. Tu función es:

1. ESCUCHAR Y COMPRENDER: Hacer preguntas relevantes sobre los síntomas del paciente
2. EVALUAR URGENCIA: Determinar si los síntomas requieren atención médica inmediata
3. RECOMENDAR: Sugerir acciones apropiadas (descanso, medicamentos de venta libre, consulta médica)
4. NO DIAGNOSTICAR: NUNCA des diagnósticos definitivos. Solo proporciona información general
5. DERIVAR: Si detectas síntomas graves o urgentes, recomienda consulta médica inmediata

IMPORTANTE:
- Sé empático y comprensivo
- Haz preguntas claras y específicas
- Si hay señales de alarma (dolor de pecho, dificultad respiratoria severa, sangrado abundante, etc.), recomienda atención inmediata
- Proporciona información educativa sobre salud general
- Recuerda que NO eres un médico y no puedes diagnosticar

SÍNTOMAS DE ALARMA (requieren atención inmediata):
- Dolor de pecho o presión
- Dificultad severa para respirar
- Alteración del estado de conciencia
- Sangrado abundante o incontrolable
- Fiebre muy alta (>40°C) que no baja
- Dolor abdominal intenso y súbito
- Signos de accidente cerebrovascular (debilidad facial, dificultad para hablar)
- Trauma grave o lesión seria

Mantén un tono profesional pero cercano, y siempre prioriza la seguridad del paciente."""

    def iniciar_conversacion(self, paciente_id, titulo="Nueva Consulta con Asistente"):
        """
        Inicia una nueva conversación con el asistente virtual
        
        Args:
            paciente_id: ID del paciente
            titulo: Título de la conversación
        
        Returns:
            ConversacionIA: Objeto de conversación creado
        """
        paciente = Paciente.objects.get(id=paciente_id)
        
        conversacion = ConversacionIA.objects.create(
            paciente=paciente,
            titulo=titulo,
            activa=True
        )
        
        # Mensaje inicial del sistema
        mensaje_sistema = MensajeIA.objects.create(
            conversacion=conversacion,
            rol='sistema',
            contenido='Conversación iniciada con el asistente virtual.',
            modelo_ia=self.modelo
        )
        
        # Mensaje de bienvenida del asistente
        contexto_paciente = self._obtener_contexto_paciente(paciente)
        
        mensaje_bienvenida = f"""¡Hola! Soy tu asistente médico virtual. Estoy aquí para ayudarte con tus consultas de salud.

Antes de comenzar, quiero conocerte un poco. Veo que:
{contexto_paciente}

¿En qué puedo ayudarte hoy? Cuéntame qué síntomas o preocupaciones de salud tienes."""
        
        MensajeIA.objects.create(
            conversacion=conversacion,
            rol='asistente',
            contenido=mensaje_bienvenida,
            modelo_ia=self.modelo
        )
        
        return conversacion
    
    def _obtener_contexto_paciente(self, paciente):
        """Obtiene información relevante del paciente para contexto"""
        contexto = []
        
        if paciente.alergias:
            contexto.append(f"- Tienes alergias a: {paciente.alergias}")
        
        if paciente.enfermedades_cronicas:
            contexto.append(f"- Padeces de: {paciente.enfermedades_cronicas}")
        
        if not contexto:
            contexto.append("- No tengo información previa de alergias o enfermedades crónicas")
        
        return "\n".join(contexto)
    
    def enviar_mensaje(self, conversacion_id, contenido_mensaje):
        """
        Envía un mensaje del paciente y obtiene respuesta del asistente
        
        Args:
            conversacion_id: ID de la conversación
            contenido_mensaje: Mensaje del paciente
        
        Returns:
            dict: Respuesta con mensaje del asistente y análisis
        """
        conversacion = ConversacionIA.objects.get(id=conversacion_id)
        paciente = conversacion.paciente
        
        # Guardar mensaje del paciente
        mensaje_paciente = MensajeIA.objects.create(
            conversacion=conversacion,
            rol='paciente',
            contenido=contenido_mensaje
        )
        
        # Analizar el mensaje del paciente
        analisis = self._analizar_mensaje(contenido_mensaje)
        mensaje_paciente.contiene_sintomas = analisis['contiene_sintomas']
        mensaje_paciente.contiene_urgencia = analisis['contiene_urgencia']
        mensaje_paciente.save()
        
        # Actualizar la conversación con los síntomas mencionados
        if analisis['sintomas_detectados']:
            sintomas_actuales = conversacion.sintomas_mencionados or ""
            nuevos_sintomas = ", ".join(analisis['sintomas_detectados'])
            if sintomas_actuales:
                conversacion.sintomas_mencionados = f"{sintomas_actuales}, {nuevos_sintomas}"
            else:
                conversacion.sintomas_mencionados = nuevos_sintomas
        
        # Actualizar nivel de urgencia si es necesario
        if analisis['nivel_urgencia'] and (not conversacion.nivel_urgencia or analisis['nivel_urgencia'] > conversacion.nivel_urgencia):
            conversacion.nivel_urgencia = analisis['nivel_urgencia']
            conversacion.requiere_atencion_medica = analisis['nivel_urgencia'] >= 7
        
        conversacion.fecha_ultima_actividad = timezone.now()
        conversacion.save()
        
        # Obtener historial de la conversación
        historial_mensajes = self._construir_historial(conversacion, paciente)
        
        # Llamar a la API de OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=historial_mensajes,
                temperature=0.7,
                max_tokens=800
            )
            
            respuesta_asistente = response.choices[0].message.content
            tokens_usados = response.usage.total_tokens
            
            # Guardar respuesta del asistente
            mensaje_asistente = MensajeIA.objects.create(
                conversacion=conversacion,
                rol='asistente',
                contenido=respuesta_asistente,
                tokens_utilizados=tokens_usados,
                modelo_ia=self.modelo
            )
            
            # Analizar si la respuesta contiene indicación de urgencia
            if self._detecta_recomendacion_urgente(respuesta_asistente):
                conversacion.requiere_atencion_medica = True
                if not conversacion.nivel_urgencia or conversacion.nivel_urgencia < 7:
                    conversacion.nivel_urgencia = 7
                conversacion.save()
            
            return {
                'exito': True,
                'mensaje': respuesta_asistente,
                'analisis': analisis,
                'requiere_atencion': conversacion.requiere_atencion_medica,
                'nivel_urgencia': conversacion.nivel_urgencia,
                'tokens_usados': tokens_usados
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'mensaje': 'Lo siento, hubo un error al procesar tu mensaje. Por favor intenta nuevamente.'
            }
    
    def _construir_historial(self, conversacion, paciente):
        """Construye el historial de mensajes para enviar a OpenAI"""
        mensajes = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Agregar contexto del paciente
        contexto = f"Información del paciente: {paciente.nombre}, {paciente.edad()} años."
        if paciente.alergias:
            contexto += f" Alergias: {paciente.alergias}."
        if paciente.enfermedades_cronicas:
            contexto += f" Enfermedades crónicas: {paciente.enfermedades_cronicas}."
        
        mensajes.append({"role": "system", "content": contexto})
        
        # Obtener los últimos 10 mensajes de la conversación (excluyendo sistema)
        ultimos_mensajes = conversacion.mensajes.exclude(rol='sistema').order_by('fecha_envio')[:10]
        
        for mensaje in ultimos_mensajes:
            if mensaje.rol == 'paciente':
                mensajes.append({"role": "user", "content": mensaje.contenido})
            elif mensaje.rol == 'asistente':
                mensajes.append({"role": "assistant", "content": mensaje.contenido})
        
        return mensajes
    
    def _analizar_mensaje(self, contenido):
        """
        Analiza el mensaje del paciente para detectar síntomas y urgencia
        
        Returns:
            dict: Análisis del mensaje
        """
        contenido_lower = contenido.lower()
        
        # Palabras clave de síntomas comunes
        sintomas_keywords = {
            'dolor': ['dolor', 'duele', 'adolorido', 'molestia'],
            'fiebre': ['fiebre', 'temperatura', 'calentura', 'febrícula'],
            'tos': ['tos', 'tosiendo', 'toser'],
            'mareo': ['mareo', 'mareado', 'vértigo', 'inestable'],
            'nausea': ['náusea', 'náuseas', 'ganas de vomitar', 'asco'],
            'vomito': ['vómito', 'vomitando', 'vomité'],
            'diarrea': ['diarrea', 'evacuaciones', 'descomposición'],
            'fatiga': ['cansancio', 'fatiga', 'cansado', 'agotado', 'débil'],
            'respiracion': ['respirar', 'respiro', 'ahogo', 'falta de aire'],
        }
        
        # Palabras clave de urgencia alta
        urgencia_keywords = [
            'dolor de pecho', 'no puedo respirar', 'sangre', 'sangrando',
            'desmayo', 'inconsciente', 'confusión', 'convulsión',
            'dolor intenso', 'no puedo moverme', 'parálisis',
            'mucho dolor', 'insoportable', 'emergencia'
        ]
        
        sintomas_detectados = []
        contiene_sintomas = False
        contiene_urgencia = False
        nivel_urgencia = 1
        
        # Detectar síntomas
        for sintoma, keywords in sintomas_keywords.items():
            if any(keyword in contenido_lower for keyword in keywords):
                sintomas_detectados.append(sintoma)
                contiene_sintomas = True
        
        # Detectar urgencia
        for keyword in urgencia_keywords:
            if keyword in contenido_lower:
                contiene_urgencia = True
                nivel_urgencia = 8
                break
        
        # Si hay síntomas pero no urgencia clara, asignar nivel medio
        if contiene_sintomas and not contiene_urgencia:
            nivel_urgencia = 4
        
        return {
            'contiene_sintomas': contiene_sintomas,
            'contiene_urgencia': contiene_urgencia,
            'nivel_urgencia': nivel_urgencia if contiene_sintomas or contiene_urgencia else None,
            'sintomas_detectados': sintomas_detectados
        }
    
    def _detecta_recomendacion_urgente(self, respuesta):
        """Detecta si la respuesta del asistente recomienda atención urgente"""
        keywords_urgentes = [
            'atención inmediata',
            'urgencia',
            'emergencia',
            'acude al médico de inmediato',
            'consulta urgente',
            'atención médica urgente',
            'servicio de emergencias'
        ]
        
        respuesta_lower = respuesta.lower()
        return any(keyword in respuesta_lower for keyword in keywords_urgentes)
    
    def finalizar_conversacion(self, conversacion_id):
        """
        Finaliza una conversación activa
        
        Args:
            conversacion_id: ID de la conversación
        """
        conversacion = ConversacionIA.objects.get(id=conversacion_id)
        conversacion.activa = False
        conversacion.save()
        
        # Mensaje de despedida
        MensajeIA.objects.create(
            conversacion=conversacion,
            rol='asistente',
            contenido='Gracias por consultar. Si tienes más preguntas, no dudes en iniciar una nueva conversación. ¡Cuídate!',
            modelo_ia=self.modelo
        )
        
        return {
            'exito': True,
            'mensaje': 'Conversación finalizada correctamente'
        }
    
    def obtener_historial(self, conversacion_id):
        """
        Obtiene el historial completo de una conversación
        
        Args:
            conversacion_id: ID de la conversación
        
        Returns:
            dict: Historial de mensajes
        """
        conversacion = ConversacionIA.objects.get(id=conversacion_id)
        mensajes = conversacion.mensajes.exclude(rol='sistema').order_by('fecha_envio')
        
        historial = []
        for mensaje in mensajes:
            historial.append({
                'id': mensaje.id,
                'rol': mensaje.rol,
                'contenido': mensaje.contenido,
                'fecha': mensaje.fecha_envio.isoformat(),
                'tokens': mensaje.tokens_utilizados
            })
        
        return {
            'conversacion_id': conversacion.id,
            'titulo': conversacion.titulo,
            'paciente': conversacion.paciente.nombre,
            'activa': conversacion.activa,
            'requiere_atencion': conversacion.requiere_atencion_medica,
            'nivel_urgencia': conversacion.nivel_urgencia,
            'sintomas': conversacion.sintomas_mencionados,
            'mensajes': historial
        }
