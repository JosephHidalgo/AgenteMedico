from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Paciente(models.Model):
    """Modelo para almacenar información de pacientes"""
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    TIPO_SANGRE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    # Información personal
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    tipo_sangre = models.CharField(max_length=3, choices=TIPO_SANGRE_CHOICES, blank=True)
    
    # Información de contacto
    telefono = models.CharField(max_length=20, help_text="Teléfono de contacto del paciente")
    email = models.EmailField(unique=True, help_text="Email único del paciente")
    direccion = models.TextField(blank=True)
    
    # Información médica básica
    alergias = models.TextField(blank=True, help_text="Alergias conocidas del paciente")
    enfermedades_cronicas = models.TextField(blank=True, help_text="Enfermedades crónicas o condiciones pre-existentes")
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"
    
    def edad(self):
        """Calcula la edad del paciente"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    def nombre_completo(self):
        """Retorna el nombre completo del paciente"""
        if self.apellido_materno:
            return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
        return f"{self.nombre} {self.apellido_paterno}"


class Medico(models.Model):
    """Modelo para almacenar información de médicos"""
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    # Información personal
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField()
    
    # Información de contacto
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.TextField(blank=True)
    
    # Información profesional
    especialidad = models.CharField(max_length=100, help_text="Especialidad médica (Cardiología, Pediatría, etc.)")
    sub_especialidad = models.CharField(max_length=100, blank=True, help_text="Sub-especialidad si aplica")
    cedula_profesional = models.CharField(max_length=50, unique=True, help_text="Cédula profesional")
    cedula_especialidad = models.CharField(max_length=50, blank=True, help_text="Cédula de especialidad")
    
    # Experiencia y formación
    universidad = models.CharField(max_length=200, blank=True)
    anos_experiencia = models.IntegerField(validators=[MinValueValidator(0)], help_text="Años de experiencia")
    biografia = models.TextField(blank=True, help_text="Biografía profesional del médico")
    
    # Disponibilidad
    activo = models.BooleanField(default=True, help_text="Si el médico está activo para consultas")
    acepta_nuevos_pacientes = models.BooleanField(default=True)
    
    # Configuración de consultas
    duracion_consulta_minutos = models.IntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(120)],
        help_text="Duración estándar de consulta en minutos"
    )
    costo_consulta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Costo de la consulta"
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"
        ordering = ['apellido_paterno', 'nombre']
    
    def __str__(self):
        return f"Dr(a). {self.nombre} {self.apellido_paterno} - {self.especialidad}"
    
    def nombre_completo(self):
        """Retorna el nombre completo del médico"""
        if self.apellido_materno:
            return f"Dr(a). {self.nombre} {self.apellido_paterno} {self.apellido_materno}"
        return f"Dr(a). {self.nombre} {self.apellido_paterno}"


class HorarioMedico(models.Model):
    """Modelo para definir los horarios de atención de los médicos"""
    
    DIAS_SEMANA_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA_CHOICES)
    hora_inicio = models.TimeField(help_text="Hora de inicio de atención")
    hora_fin = models.TimeField(help_text="Hora de fin de atención")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Horario Médico"
        verbose_name_plural = "Horarios Médicos"
        ordering = ['medico', 'dia_semana', 'hora_inicio']
        unique_together = ['medico', 'dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.medico.nombre_completo()} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


class Cita(models.Model):
    """Modelo para agendar citas médicas"""
    
    ESTADO_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('EXPIRADA', 'Expirada'),
    ]
    
    TIPO_CONSULTA_CHOICES = [
        ('primera_vez', 'Primera Vez'),
        ('seguimiento', 'Seguimiento'),
        ('urgencia', 'Urgencia'),
        ('control', 'Control'),
    ]
    
    # Relaciones principales
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='citas')
    consulta = models.OneToOneField(
        'Consulta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cita',
        help_text="Consulta asociada una vez realizada la cita"
    )
    
    # Información de la cita
    fecha = models.DateField(help_text="Fecha de la cita")
    hora = models.TimeField(help_text="Hora de la cita")
    duracion_minutos = models.IntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(180)],
        help_text="Duración estimada en minutos"
    )
    tipo_consulta = models.CharField(max_length=20, choices=TIPO_CONSULTA_CHOICES, default='primera_vez')
    motivo = models.TextField(help_text="Motivo de la cita")
    sintomas_iniciales = models.TextField(blank=True, help_text="Síntomas mencionados en el chat")
    notas_paciente = models.TextField(blank=True, help_text="Notas adicionales del paciente")
    consultorio = models.CharField(max_length=50, blank=True, help_text="Número o nombre del consultorio")
    
    # Estado y gestión
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='AGENDADA')
    confirmada_por_paciente = models.BooleanField(default=False)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    
    # Cancelación
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
    motivo_cancelacion = models.TextField(blank=True)
    
    # Recordatorios
    recordatorio_enviado = models.BooleanField(default=False)
    fecha_recordatorio = models.DateTimeField(null=True, blank=True)
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['fecha', 'hora']
        indexes = [
            models.Index(fields=['fecha', 'hora', 'medico']),
            models.Index(fields=['paciente', 'estado']),
        ]
        unique_together = [['medico', 'fecha', 'hora']]  # No permitir citas duplicadas
    
    def __str__(self):
        from datetime import datetime
        return f"Cita: {self.paciente} con {self.medico.nombre_completo()} - {self.fecha.strftime('%d/%m/%Y')} {self.hora.strftime('%H:%M')}"
    
    def esta_disponible(self):
        """Verifica si la cita sigue disponible (no cancelada ni completada)"""
        return self.estado == 'AGENDADA'
    
    def puede_cancelar(self):
        """Verifica si la cita puede ser cancelada"""
        from django.utils import timezone
        from datetime import datetime
        # Se puede cancelar si está agendada y falta más de 2 horas
        if self.estado == 'AGENDADA':
            fecha_hora_cita = datetime.combine(self.fecha, self.hora)
            # Hacer timezone aware
            if timezone.is_naive(fecha_hora_cita):
                fecha_hora_cita = timezone.make_aware(fecha_hora_cita)
            horas_restantes = (fecha_hora_cita - timezone.now()).total_seconds() / 3600
            return horas_restantes > 2
        return False


class HistorialMedico(models.Model):
    """Modelo para el historial médico del paciente"""
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historiales')
    fecha_evento = models.DateField()
    tipo_evento = models.CharField(max_length=100, help_text="Tipo de evento médico (cirugía, hospitalización, etc.)")
    descripcion = models.TextField()
    institucion = models.CharField(max_length=200, blank=True, help_text="Institución donde ocurrió el evento")
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial Médico"
        verbose_name_plural = "Historiales Médicos"
        ordering = ['-fecha_evento']
    
    def __str__(self):
        return f"{self.paciente} - {self.tipo_evento} ({self.fecha_evento})"


class Consulta(models.Model):
    """Modelo para registrar consultas médicas"""
    
    ESTADO_CHOICES = [
        ('programada', 'Programada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    medico = models.ForeignKey(
        Medico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultas',
        help_text="Médico que realiza la consulta"
    )
    fecha_hora = models.DateTimeField()
    motivo_consulta = models.TextField(help_text="Razón principal de la consulta")
    sintomas = models.TextField(blank=True, help_text="Síntomas reportados por el paciente")
    
    # Signos vitales
    presion_arterial_sistolica = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(250)]
    )
    presion_arterial_diastolica = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(150)]
    )
    frecuencia_cardiaca = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(220)],
        help_text="Latidos por minuto"
    )
    temperatura = models.DecimalField(
        max_digits=4, 
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(35.0), MaxValueValidator(42.0)],
        help_text="Temperatura corporal en °C"
    )
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(500.0)],
        help_text="Peso en kg"
    )
    altura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.40), MaxValueValidator(2.50)],
        help_text="Altura en metros"
    )
    
    # Observaciones y estado
    observaciones = models.TextField(blank=True, help_text="Observaciones del médico")
    plan_tratamiento = models.TextField(blank=True, help_text="Plan de tratamiento recomendado")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programada')
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"Consulta de {self.paciente} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def imc(self):
        """Calcula el índice de masa corporal"""
        if self.peso and self.altura:
            return round(float(self.peso) / (float(self.altura) ** 2), 2)
        return None


class Diagnostico(models.Model):
    """Modelo para diagnósticos asociados a consultas"""
    
    TIPO_CHOICES = [
        ('principal', 'Principal'),
        ('secundario', 'Secundario'),
        ('diferencial', 'Diferencial'),
    ]
    
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='diagnosticos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='principal')
    codigo_cie10 = models.CharField(max_length=10, blank=True, help_text="Código CIE-10")
    nombre = models.CharField(max_length=200, help_text="Nombre del diagnóstico")
    descripcion = models.TextField(blank=True)
    notas = models.TextField(blank=True, help_text="Notas adicionales del médico")
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"
        ordering = ['tipo', '-fecha_registro']
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Medicamento(models.Model):
    """Catálogo de medicamentos"""
    
    nombre_comercial = models.CharField(max_length=200)
    nombre_generico = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100, help_text="Categoría del medicamento (antibiótico, analgésico, etc.)")
    presentacion = models.CharField(max_length=100, help_text="Presentación (tabletas, jarabe, inyectable, etc.)")
    concentracion = models.CharField(max_length=100, help_text="Concentración (500mg, 10ml, etc.)")
    descripcion = models.TextField(blank=True)
    contraindicaciones = models.TextField(blank=True)
    efectos_secundarios = models.TextField(blank=True)
    
    # Metadatos
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"
        ordering = ['nombre_generico']
    
    def __str__(self):
        return f"{self.nombre_comercial} ({self.nombre_generico}) - {self.concentracion}"


class Prescripcion(models.Model):
    """Modelo para prescripciones médicas"""
    
    FRECUENCIA_CHOICES = [
        ('cada_4h', 'Cada 4 horas'),
        ('cada_6h', 'Cada 6 horas'),
        ('cada_8h', 'Cada 8 horas'),
        ('cada_12h', 'Cada 12 horas'),
        ('cada_24h', 'Cada 24 horas'),
        ('segun_necesidad', 'Según necesidad'),
    ]
    
    VIA_ADMINISTRACION_CHOICES = [
        ('oral', 'Oral'),
        ('sublingual', 'Sublingual'),
        ('topica', 'Tópica'),
        ('intravenosa', 'Intravenosa'),
        ('intramuscular', 'Intramuscular'),
        ('subcutanea', 'Subcutánea'),
        ('rectal', 'Rectal'),
        ('oftalmica', 'Oftálmica'),
        ('otica', 'Ótica'),
        ('nasal', 'Nasal'),
    ]
    
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='prescripciones')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT, related_name='prescripciones')
    
    # Detalles de la prescripción
    dosis = models.CharField(max_length=100, help_text="Dosis a administrar")
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES)
    via_administracion = models.CharField(max_length=20, choices=VIA_ADMINISTRACION_CHOICES)
    duracion_dias = models.IntegerField(validators=[MinValueValidator(1)], help_text="Duración del tratamiento en días")
    
    # Instrucciones
    instrucciones = models.TextField(blank=True, help_text="Instrucciones especiales para el paciente")
    antes_despues_comida = models.CharField(
        max_length=20,
        choices=[
            ('antes', 'Antes de comer'),
            ('despues', 'Después de comer'),
            ('con', 'Con alimentos'),
            ('indistinto', 'Indistinto'),
        ],
        default='indistinto'
    )
    
    # Fechas
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Prescripción"
        verbose_name_plural = "Prescripciones"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.medicamento.nombre_comercial} - {self.dosis} {self.frecuencia}"


class ConversacionIA(models.Model):
    """Modelo para registrar conversaciones con el asistente de IA"""
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='conversaciones_ia')
    consulta = models.ForeignKey(
        Consulta, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='conversaciones_ia',
        help_text="Consulta asociada si la conversación deriva en una"
    )
    
    titulo = models.CharField(max_length=200, help_text="Título o resumen de la conversación")
    
    # Estado de la conversación
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actividad = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True)
    
    # Contexto y análisis
    sintomas_mencionados = models.TextField(blank=True, help_text="Síntomas que el paciente mencionó")
    temas_discutidos = models.TextField(blank=True, help_text="Temas principales de la conversación")
    requiere_atencion_medica = models.BooleanField(
        default=False,
        help_text="Si la IA determina que requiere atención médica urgente"
    )
    nivel_urgencia = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Nivel de urgencia de 1 a 10"
    )
    
    class Meta:
        verbose_name = "Conversación IA"
        verbose_name_plural = "Conversaciones IA"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.paciente} - {self.titulo}"


class MensajeIA(models.Model):
    """Modelo para mensajes individuales en conversaciones con IA"""
    
    ROL_CHOICES = [
        ('paciente', 'Paciente'),
        ('asistente', 'Asistente IA'),
        ('sistema', 'Sistema'),
    ]
    
    conversacion = models.ForeignKey(ConversacionIA, on_delete=models.CASCADE, related_name='mensajes')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    contenido = models.TextField()
    
    # Metadatos del mensaje
    fecha_envio = models.DateTimeField(auto_now_add=True)
    tokens_utilizados = models.IntegerField(null=True, blank=True, help_text="Tokens utilizados por el modelo de IA")
    modelo_ia = models.CharField(max_length=100, blank=True, help_text="Modelo de IA utilizado (ej: GPT-4, Claude, etc.)")
    
    # Análisis del mensaje
    contiene_sintomas = models.BooleanField(default=False)
    contiene_urgencia = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Mensaje IA"
        verbose_name_plural = "Mensajes IA"
        ordering = ['fecha_envio']
    
    def __str__(self):
        return f"{self.rol} - {self.fecha_envio.strftime('%d/%m/%Y %H:%M')}"


class Archivo(models.Model):
    """Modelo para almacenar archivos adjuntos (estudios, resultados, etc.)"""
    
    TIPO_CHOICES = [
        ('laboratorio', 'Resultado de Laboratorio'),
        ('imagen', 'Imagen Médica'),
        ('receta', 'Receta Médica'),
        ('estudio', 'Estudio Médico'),
        ('documento', 'Documento General'),
        ('otro', 'Otro'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='archivos')
    consulta = models.ForeignKey(
        Consulta, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='archivos'
    )
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='archivos_medicos/%Y/%m/')
    
    # Metadatos
    fecha_subida = models.DateTimeField(auto_now_add=True)
    tamanio = models.IntegerField(help_text="Tamaño del archivo en bytes")
    
    class Meta:
        verbose_name = "Archivo"
        verbose_name_plural = "Archivos"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre} - {self.paciente}"
