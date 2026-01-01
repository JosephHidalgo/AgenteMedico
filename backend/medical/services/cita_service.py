"""
Servicio para gestión de citas médicas
"""
from django.db import transaction
from django.utils import timezone
from datetime import datetime, date as dt_date
from ..models import Cita, Paciente, Medico
import logging

logger = logging.getLogger(__name__)


class CitaService:
    """
    Servicio para crear y gestionar citas médicas
    Incluye lógica de negocio para:
    - Crear/reutilizar pacientes por email
    - Validar disponibilidad de horarios
    - Sugerir horarios alternativos
    """
    
    @staticmethod
    def get_or_create_paciente(datos_paciente):
        """
        Busca un paciente por email, si existe lo retorna, sino lo crea.
        
        Args:
            datos_paciente (dict): Diccionario con datos del paciente
                - nombre: str
                - apellido_paterno: str
                - apellido_materno: str
                - fecha_nacimiento: date
                - sexo: str
                - email: str
                - telefono: str
        
        Returns:
            tuple: (Paciente, created:bool)
        """
        email = datos_paciente['email'].lower().strip()
        
        # Intentar encontrar paciente existente por email
        try:
            paciente = Paciente.objects.get(email=email)
            # Actualizar datos si es necesario
            paciente.telefono = datos_paciente['telefono']
            paciente.save(update_fields=['telefono', 'fecha_actualizacion'])
            return paciente, False
        except Paciente.DoesNotExist:
            # Crear nuevo paciente
            paciente = Paciente.objects.create(
                nombre=datos_paciente['nombre'],
                apellido_paterno=datos_paciente['apellido_paterno'],
                apellido_materno=datos_paciente['apellido_materno'],
                fecha_nacimiento=datos_paciente['fecha_nacimiento'],
                sexo=datos_paciente['sexo'],
                email=email,
                telefono=datos_paciente['telefono']
            )
            return paciente, True
    
    @staticmethod
    def validar_disponibilidad(medico_id, fecha, hora):
        """
        Valida si un horario está disponible para un médico
        
        Args:
            medico_id (int): ID del médico
            fecha (date): Fecha de la cita
            hora (time): Hora de la cita
        
        Returns:
            tuple: (disponible:bool, mensaje:str)
        """
        # Validar que la fecha sea futura
        if fecha < dt_date.today():
            return False, "La fecha de la cita debe ser futura"
        
        # Validar que el médico existe y está disponible
        try:
            medico = Medico.objects.get(id=medico_id, activo=True)
        except Medico.DoesNotExist:
            return False, "El médico no existe o no está disponible"
        
        # Validar que no haya otra cita en ese horario
        cita_existente = Cita.objects.filter(
            medico_id=medico_id,
            fecha=fecha,
            hora=hora,
            estado='AGENDADA'
        ).exists()
        
        if cita_existente:
            return False, "Este horario ya está ocupado"
        
        return True, "Horario disponible"
    
    @staticmethod
    def obtener_horarios_alternativos(medico_id, fecha, hora_preferida=None, cantidad=5):
        """
        Obtiene horarios alternativos disponibles para un médico
        
        Args:
            medico_id (int): ID del médico
            fecha (date): Fecha base para buscar
            hora_preferida (time, optional): Hora preferida como referencia
            cantidad (int): Cantidad de alternativas a retornar
        
        Returns:
            list: Lista de diccionarios con fecha y hora disponibles
        """
        from datetime import timedelta, time
        
        medico = Medico.objects.get(id=medico_id)
        alternativas = []
        
        # Horarios de trabajo estándar (9 AM - 5 PM cada 30 min)
        horarios_base = [
            time(9, 0), time(9, 30), time(10, 0), time(10, 30),
            time(11, 0), time(11, 30), time(12, 0), time(12, 30),
            time(13, 0), time(13, 30), time(14, 0), time(14, 30),
            time(15, 0), time(15, 30), time(16, 0), time(16, 30)
        ]
        
        # Buscar en los próximos 7 días
        fecha_busqueda = fecha
        dias_buscados = 0
        
        while len(alternativas) < cantidad and dias_buscados < 7:
            if fecha_busqueda >= dt_date.today():
                for hora in horarios_base:
                    # Verificar disponibilidad
                    disponible, _ = CitaService.validar_disponibilidad(
                        medico_id, fecha_busqueda, hora
                    )
                    
                    if disponible:
                        alternativas.append({
                            'fecha': fecha_busqueda,
                            'hora': hora,
                            'fecha_str': fecha_busqueda.strftime('%d/%m/%Y'),
                            'hora_str': hora.strftime('%H:%M')
                        })
                        
                        if len(alternativas) >= cantidad:
                            break
            
            fecha_busqueda += timedelta(days=1)
            dias_buscados += 1
        
        return alternativas
    
    @staticmethod
    @transaction.atomic
    def crear_cita(datos_paciente, datos_cita):
        """
        Crea una nueva cita médica y envía confirmación por email
        
        Args:
            datos_paciente (dict): Datos del paciente
            datos_cita (dict): Datos de la cita
                - medico_id: int
                - fecha: date
                - hora: time
                - motivo: str
                - sintomas_iniciales: str (opcional)
        
        Returns:
            tuple: (Cita, created:bool, mensaje:str)
        
        Raises:
            ValueError: Si los datos son inválidos o el horario no está disponible
        """
        # Validar disponibilidad
        disponible, mensaje = CitaService.validar_disponibilidad(
            datos_cita['medico_id'],
            datos_cita['fecha'],
            datos_cita['hora']
        )
        
        print("\n" + "="*80)
        print("🚀 INICIANDO CREACIÓN DE CITA")
        print("="*80)
        logger.info(f"=== CREANDO CITA ===")
        logger.info(f"Disponibilidad validada: {disponible}")
        
        if not disponible:
            raise ValueError(mensaje)
        
        # Obtener o crear paciente
        paciente, paciente_creado = CitaService.get_or_create_paciente(datos_paciente)
        
        # Obtener médico
        medico = Medico.objects.get(id=datos_cita['medico_id'])
        
        # Asignar consultorio (simple: usar ID del médico como número)
        consultorio = f"Consultorio {medico.id}"
        
        # Crear cita
        cita = Cita.objects.create(
            paciente=paciente,
            medico=medico,
            fecha=datos_cita['fecha'],
            hora=datos_cita['hora'],
            duracion_minutos=medico.duracion_consulta_minutos,
            motivo=datos_cita['motivo'],
            sintomas_iniciales=datos_cita.get('sintomas_iniciales', ''),
            consultorio=consultorio,
            estado='AGENDADA'
        )
        
        print(f"✅ Cita #{cita.id} creada exitosamente")
        print(f"   Paciente: {paciente.email}")
        print(f"   Médico: {medico.nombre} {medico.apellido_paterno}")
        print(f"   Fecha: {datos_cita['fecha']}")
        logger.info(f"Cita #{cita.id} creada exitosamente para {paciente.email}")
        
        # Enviar email de confirmación con PDF
        print(f"\n📧 Intentando enviar email de confirmación...")
        logger.info(f"Intentando enviar email de confirmación a {paciente.email}...")
        try:
            from .email_service import EmailService
            email_service = EmailService()
            resultado_email = email_service.enviar_confirmacion_cita(cita)
            
            if resultado_email['exito']:
                print(f"✅ EMAIL ENVIADO EXITOSAMENTE!")
                print(f"   Email ID: {resultado_email.get('email_id')}")
                logger.info(f"Email de confirmación enviado para cita {cita.id}")
                mensaje_final = "Cita creada exitosamente. Email de confirmación enviado."
            else:
                print(f"⚠️  ERROR al enviar email: {resultado_email['mensaje']}")
                logger.warning(f"Error al enviar email para cita {cita.id}: {resultado_email['mensaje']}")
                mensaje_final = "Cita creada exitosamente, pero hubo un problema al enviar el email."
        except Exception as e:
            print(f"❌ EXCEPCIÓN al enviar email: {str(e)}")
            import traceback
            traceback.print_exc()
            logger.error(f"Error inesperado al enviar email para cita {cita.id}: {str(e)}")
            mensaje_final = "Cita creada exitosamente"
        
        print("="*80)
        print(f"✅ PROCESO COMPLETADO: {mensaje_final}")
        print("="*80 + "\n")
        
        if paciente_creado:
            mensaje_final += " (nuevo paciente registrado)"
        
        return cita, True, mensaje_final
    
    @staticmethod
    def cancelar_cita(cita_id, motivo=''):
        """
        Cancela una cita existente
        
        Args:
            cita_id (int): ID de la cita
            motivo (str): Motivo de cancelación
        
        Returns:
            tuple: (success:bool, mensaje:str)
        """
        try:
            cita = Cita.objects.get(id=cita_id)
            
            if not cita.puede_cancelar():
                return False, "Esta cita no puede ser cancelada (ya pasó o está muy próxima)"
            
            cita.estado = 'CANCELADA'
            cita.fecha_cancelacion = timezone.now()
            cita.motivo_cancelacion = motivo
            cita.save()
            
            return True, "Cita cancelada exitosamente"
            
        except Cita.DoesNotExist:
            return False, "La cita no existe"
    
    @staticmethod
    def obtener_citas_proximas(medico_id=None, paciente_id=None, limite=10):
        """
        Obtiene las próximas citas agendadas
        
        Args:
            medico_id (int, optional): Filtrar por médico
            paciente_id (int, optional): Filtrar por paciente
            limite (int): Cantidad máxima de resultados
        
        Returns:
            QuerySet: Citas filtradas y ordenadas
        """
        hoy = dt_date.today()
        
        queryset = Cita.objects.filter(
            fecha__gte=hoy,
            estado='AGENDADA'
        ).select_related('paciente', 'medico')
        
        if medico_id:
            queryset = queryset.filter(medico_id=medico_id)
        
        if paciente_id:
            queryset = queryset.filter(paciente_id=paciente_id)
        
        return queryset.order_by('fecha', 'hora')[:limite]
