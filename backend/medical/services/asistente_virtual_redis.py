"""
Servicio de Asistente Virtual con OpenAI ChatGPT y Redis
Este módulo maneja todas las interacciones con la API de OpenAI usando Redis para cache
"""

from openai import OpenAI
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
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
   - Una vez definida la especialidad, SOLICITA sus datos personales EN ESTE ORDEN:
     * Nombre completo (nombre y apellidos)
     * Edad
     * Email
     * Teléfono
   - Solicita UN dato a la vez, espera la respuesta antes de pedir el siguiente
   - DESPUÉS de recopilar TODOS los datos (nombre, apellidos, edad, email, teléfono), di EXACTAMENTE:
     "Perfecto, ya tengo toda tu información. Haz clic en el botón 'Crear Cita Ahora' para confirmar tu cita."
   - NO menciones fechas u horas específicas, el sistema las asignará automáticamente
   - NO intentes crear la cita tú mismo, el usuario debe hacer clic en el botón

4. **DETECCIÓN DE INTENCIÓN**:
   - Identifica si el usuario quiere: [SINTOMAS] o [AGENDAR_CITA]
   - Marca claramente la intención en tu respuesta

5. **SÉ CONCISO Y DIRECTO**:
   - Respuestas claras y breves
   - Usa emojis moderadamente
   - Guía al usuario paso a paso
   - Solicita UN dato a la vez

6. **IMPORTANTE**:
   - NO diagnostiques
   - Si detectas síntomas graves, recomienda atención inmediata
   - Sé empático pero profesional
   - NO inventes fechas u horas de citas, el sistema las asignará

**SÍNTOMAS DE ALARMA** (requieren atención urgente):
- Dolor de pecho intenso
- Dificultad severa para respirar
- Sangrado abundante
- Alteración de conciencia
- Fiebre >40°C persistente

**ESPECIALIDADES DISPONIBLES**:
- Medicina General
- Cardiología
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

Puedo evaluar tus síntomas o ayudarte a agendar una cita médica.
¿En qué puedo ayudarte hoy? :)"""
        
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
            # 'endocrinología': 'Endocrinología',
            # 'endocrinologia': 'Endocrinología',
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
    
    def extraer_datos_paciente(self, conversacion_id):
        """
        Extrae los datos del paciente de la conversación usando IA
        
        Args:
            conversacion_id (str): UUID de la conversación
        
        Returns:
            dict: Datos extraídos del paciente o None si no hay suficiente información
        """
        conversacion = self.obtener_conversacion(conversacion_id)
        
        if not conversacion:
            return None
        
        # Obtener TODA la conversación excluyendo el system prompt
        mensajes_conversacion = [
            f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
            for m in conversacion['mensajes']
            if m['role'] != 'system'
        ]
        
        texto_completo = '\n'.join(mensajes_conversacion)
        
        print(f"[DEBUG] Conversación para extracción:\n{texto_completo[:500]}...")
        
        # Usar OpenAI para extraer datos estructurados
        prompt_extraccion = f"""Analiza la siguiente conversación completa entre un usuario y un asistente médico.
Extrae los datos personales del paciente que fueron mencionados.

CONVERSACIÓN:
{texto_completo}

Extrae los siguientes datos del paciente:
- Nombre completo (separar en nombre, apellido_paterno, apellido_materno si están disponibles)
- Edad (número)
- Email 
- Teléfono

IMPORTANTE:
- Busca la información en las respuestas del Usuario
- Si el apellido materno no fue mencionado, usa cadena vacía ""
- La edad debe ser un número
- El teléfono puede tener cualquier formato

Responde ÚNICAMENTE en formato JSON válido, sin texto adicional.

Si encontraste todos los datos mínimos (nombre, edad, email, teléfono), responde así:
{{
    "nombre": "nombre_encontrado",
    "apellido_paterno": "apellido_encontrado",
    "apellido_materno": "apellido_materno_o_vacio",
    "edad": numero,
    "email": "email@ejemplo.com",
    "telefono": "numero_telefono"
}}

Si NO encontraste los datos mínimos, responde SOLO:
{{"datos_completos": false}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {
                        'role': 'system',
                        'content': 'Eres un asistente experto en extraer datos estructurados de conversaciones. Respondes SOLO en formato JSON válido, sin explicaciones adicionales.'
                    },
                    {
                        'role': 'user',
                        'content': prompt_extraccion
                    }
                ],
                max_tokens=400,
                temperature=0.1
            )
            
            respuesta_json = response.choices[0].message.content.strip()
            print(f"[DEBUG] Respuesta de extracción: {respuesta_json}")
            
            # Limpiar markdown si existe
            if '```json' in respuesta_json:
                respuesta_json = respuesta_json.split('```json')[1].split('```')[0].strip()
            elif '```' in respuesta_json:
                respuesta_json = respuesta_json.split('```')[1].split('```')[0].strip()
            
            datos = json.loads(respuesta_json)
            print(f"[DEBUG] Datos parseados: {datos}")
            
            # Validar que tenga los datos mínimos
            if datos.get('datos_completos') == False:
                print(f"[DEBUG] La IA indicó que no hay datos completos")
                return None
            
            # Validar campos requeridos
            campos_requeridos = ['nombre', 'edad', 'email', 'telefono']
            if not all([datos.get(campo) for campo in campos_requeridos]):
                print(f"[DEBUG] Faltan campos requeridos. Datos: {datos}")
                return None
            
            # Asegurar que apellido_paterno esté presente (puede estar vacío)
            if 'apellido_paterno' not in datos:
                datos['apellido_paterno'] = ''
            if 'apellido_materno' not in datos:
                datos['apellido_materno'] = ''
            
            print(f"[DEBUG] Datos extraídos exitosamente: {datos}")
            
            # Guardar en conversación
            conversacion['datos_paciente'] = datos
            self.guardar_conversacion(conversacion)
            
            return datos
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error al parsear JSON: {e}")
            print(f"[ERROR] Respuesta recibida: {respuesta_json}")
            return None
        except Exception as e:
            print(f"[ERROR] Error al extraer datos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def crear_cita_desde_conversacion(self, conversacion_id):
        """
        Crea una cita en la base de datos basándose en la conversación
        
        Args:
            conversacion_id (str): UUID de la conversación
        
        Returns:
            dict: Resultado de la creación de la cita
        """
        from ..models import Paciente, Medico, Cita
        
        print(f"[DEBUG] Intentando crear cita para conversacion_id: {conversacion_id}")
        
        conversacion = self.obtener_conversacion(conversacion_id)
        
        if not conversacion:
            print(f"[DEBUG] Conversación no encontrada")
            return {
                'exito': False,
                'error': 'Conversación no encontrada o expirada'
            }
        
        print(f"[DEBUG] Conversación encontrada: {conversacion.get('conversacion_id')}")
        
        # Extraer datos si no están disponibles
        datos_paciente = conversacion.get('datos_paciente')
        print(f"[DEBUG] Datos paciente en conversación: {datos_paciente}")
        
        if not datos_paciente:
            print(f"[DEBUG] Intentando extraer datos del paciente...")
            datos_paciente = self.extraer_datos_paciente(conversacion_id)
            print(f"[DEBUG] Datos extraídos: {datos_paciente}")
        
        if not datos_paciente:
            print(f"[DEBUG] No se pudieron extraer datos del paciente")
            return {
                'exito': False,
                'error': 'No se pudieron extraer los datos completos del paciente. Asegúrate de proporcionar: nombre completo, edad, email y teléfono.'
            }
        
        especialidad = conversacion.get('especialidad_sugerida')
        print(f"[DEBUG] Especialidad sugerida: {especialidad}")
        
        if not especialidad:
            print(f"[DEBUG] No hay especialidad definida")
            return {
                'exito': False,
                'error': 'No se ha determinado la especialidad requerida. Por favor, menciona qué tipo de médico necesitas.'
            }
        
        try:
            # Calcular fecha de nacimiento aproximada
            email = datos_paciente.get('email')
            edad = datos_paciente.get('edad', 30)
            fecha_nacimiento = (datetime.now() - timedelta(days=edad*365)).date()
            
            print(f"[DEBUG] Email del paciente: {email}")
            
            # Buscar médico disponible de la especialidad
            print(f"[DEBUG] Buscando médico de especialidad: {especialidad}")
            
            # Intentar búsqueda exacta primero
            medico = Medico.objects.filter(
                especialidad=especialidad,
                activo=True,
                acepta_nuevos_pacientes=True
            ).first()
            
            # Si no encuentra, intentar búsqueda sin acentos (case insensitive)
            if not medico:
                print(f"[DEBUG] No se encontró con búsqueda exacta, intentando sin acentos...")
                # Normalizar especialidad removiendo acentos
                from unicodedata import normalize
                especialidad_normalizada = ''.join(
                    c for c in normalize('NFD', especialidad)
                    if not c.isspace() and ord(c) < 0x300 or ord(c) > 0x36f
                ).lower()
                
                print(f"[DEBUG] Especialidad normalizada: {especialidad_normalizada}")
                
                # Buscar médicos y filtrar manualmente
                medicos_disponibles = Medico.objects.filter(
                    activo=True,
                    acepta_nuevos_pacientes=True
                )
                
                for m in medicos_disponibles:
                    esp_medico_normalizada = ''.join(
                        c for c in normalize('NFD', m.especialidad)
                        if not c.isspace() and ord(c) < 0x300 or ord(c) > 0x36f
                    ).lower()
                    
                    if especialidad_normalizada == esp_medico_normalizada:
                        medico = m
                        print(f"[DEBUG] Médico encontrado con búsqueda normalizada: {m.especialidad}")
                        break
            
            if not medico:
                print(f"[DEBUG] No se encontró médico de {especialidad}")
                return {
                    'exito': False,
                    'error': f'No hay médicos disponibles de {especialidad} en este momento'
                }
            
            print(f"[DEBUG] Médico encontrado: {medico.nombre_completo()}")
            
            # Crear la cita para el siguiente día hábil
            # Buscar un horario disponible
            hoy = datetime.now().date()
            fecha_cita = hoy + timedelta(days=1)
            
            # Si es fin de semana, mover a lunes
            while fecha_cita.weekday() >= 5:  # 5=Sábado, 6=Domingo
                fecha_cita += timedelta(days=1)
            
            # Buscar una hora disponible para ese médico
            horas_disponibles = ['09:00:00', '10:00:00', '11:00:00', '14:00:00', '15:00:00', '16:00:00', '17:00:00']
            hora_asignada = None
            
            print(f"[DEBUG] Buscando horario disponible para {medico.nombre_completo()} el {fecha_cita}")
            
            for hora in horas_disponibles:
                # Verificar si ya existe una cita en ese horario
                cita_existente = Cita.objects.filter(
                    medico=medico,
                    fecha=fecha_cita,
                    hora=hora
                ).exists()
                
                if not cita_existente:
                    hora_asignada = hora
                    print(f"[DEBUG] Horario disponible encontrado: {hora}")
                    break
            
            # Si no hay horarios disponibles ese día, intentar el siguiente día
            intentos = 0
            max_intentos = 10  # Buscar hasta 10 días
            
            while not hora_asignada and intentos < max_intentos:
                fecha_cita += timedelta(days=1)
                
                # Saltar fines de semana
                while fecha_cita.weekday() >= 5:
                    fecha_cita += timedelta(days=1)
                
                print(f"[DEBUG] Intentando siguiente fecha: {fecha_cita}")
                
                for hora in horas_disponibles:
                    cita_existente = Cita.objects.filter(
                        medico=medico,
                        fecha=fecha_cita,
                        hora=hora
                    ).exists()
                    
                    if not cita_existente:
                        hora_asignada = hora
                        print(f"[DEBUG] Horario disponible encontrado: {hora}")
                        break
                
                intentos += 1
            
            if not hora_asignada:
                print(f"[DEBUG] No se encontró horario disponible en los próximos {max_intentos} días")
                return {
                    'exito': False,
                    'error': f'No hay horarios disponibles para {medico.nombre_completo()} en los próximos días. Por favor, contacta directamente al consultorio.'
                }
            
            print(f"[DEBUG] Fecha de cita calculada: {fecha_cita} a las {hora_asignada}")
            
            # Convertir hora string a objeto time
            hora_obj = datetime.strptime(hora_asignada, '%H:%M:%S').time()
            hora_12h = hora_obj.strftime('%I:%M %p')
            
            # Preparar datos para el servicio de creación de citas
            datos_paciente_servicio = {
                'nombre': datos_paciente.get('nombre', ''),
                'apellido_paterno': datos_paciente.get('apellido_paterno', ''),
                'apellido_materno': datos_paciente.get('apellido_materno', ''),
                'fecha_nacimiento': fecha_nacimiento,
                'sexo': 'O',  # Otro por defecto
                'email': email,
                'telefono': datos_paciente.get('telefono', ''),
            }
            
            datos_cita_servicio = {
                'medico_id': medico.id,
                'fecha': fecha_cita,
                'hora': hora_obj,  # Pasar como objeto time, no string
                'motivo': f'Consulta por síntomas. Especialidad: {especialidad}',
                'sintomas_iniciales': conversacion.get('sintomas', '')
            }
            
            print(f"[DEBUG] Usando CitaService para crear cita y enviar email...")
            
            # Usar el servicio de citas que incluye envío de email
            from .cita_service import CitaService
            
            try:
                cita, creada, mensaje_servicio = CitaService.crear_cita(
                    datos_paciente_servicio, 
                    datos_cita_servicio
                )
                
                print(f"[DEBUG] Cita creada exitosamente: ID={cita.id}")
                print(f"[DEBUG] Mensaje del servicio: {mensaje_servicio}")
                
            except ValueError as e:
                print(f"[ERROR] Error de validación: {str(e)}")
                return {
                    'exito': False,
                    'error': str(e)
                }
            
            # Actualizar conversación
            conversacion['cita_creada'] = {
                'cita_id': cita.id,
                'paciente': cita.paciente.nombre_completo(),
                'medico': cita.medico.nombre_completo(),
                'fecha': str(fecha_cita),
                'hora': hora_12h
            }
            self.guardar_conversacion(conversacion)
            
            return {
                'exito': True,
                'cita_id': cita.id,
                'paciente': cita.paciente.nombre_completo(),
                'medico': cita.medico.nombre_completo(),
                'especialidad': cita.medico.especialidad,
                'fecha': str(fecha_cita),
                'hora': hora_12h,
                'consultorio': cita.consultorio,
                'mensaje': mensaje_servicio  # Incluye si el email fue enviado
            }
            
        except Exception as e:
            print(f"[ERROR] Error al crear la cita: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'exito': False,
                'error': f'Error al crear la cita: {str(e)}'
            }
