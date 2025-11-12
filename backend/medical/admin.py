from django.contrib import admin
from .models import (
    Paciente, Medico, HorarioMedico, Cita, HistorialMedico, Consulta, Diagnostico,
    Medicamento, Prescripcion, ConversacionIA, MensajeIA, Archivo
)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido_paterno', 'fecha_nacimiento', 'sexo', 'tipo_sangre', 'activo', 'fecha_registro']
    list_filter = ['sexo', 'tipo_sangre', 'activo', 'fecha_registro']
    search_fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'email', 'telefono']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento', 'sexo', 'tipo_sangre')
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'email', 'direccion')
        }),
        ('Información Médica', {
            'fields': ('alergias', 'enfermedades_cronicas')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_registro', 'fecha_actualizacion')
        }),
    )


@admin.register(HistorialMedico)
class HistorialMedicoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'tipo_evento', 'fecha_evento', 'institucion']
    list_filter = ['tipo_evento', 'fecha_evento']
    search_fields = ['paciente__nombre', 'paciente__apellido_paterno', 'tipo_evento', 'descripcion']
    readonly_fields = ['fecha_registro']


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'fecha_hora', 'estado', 'motivo_consulta_corto']
    list_filter = ['estado', 'fecha_hora', 'medico']
    search_fields = ['paciente__nombre', 'paciente__apellido_paterno', 'medico__nombre', 'medico__apellido_paterno', 'motivo_consulta']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    date_hierarchy = 'fecha_hora'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('paciente', 'medico', 'fecha_hora', 'estado')
        }),
        ('Motivo y Síntomas', {
            'fields': ('motivo_consulta', 'sintomas')
        }),
        ('Signos Vitales', {
            'fields': (
                ('presion_arterial_sistolica', 'presion_arterial_diastolica'),
                'frecuencia_cardiaca',
                'temperatura',
                ('peso', 'altura')
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones', 'plan_tratamiento')
        }),
        ('Metadatos', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def motivo_consulta_corto(self, obj):
        return obj.motivo_consulta[:50] + '...' if len(obj.motivo_consulta) > 50 else obj.motivo_consulta
    motivo_consulta_corto.short_description = 'Motivo'


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'consulta', 'tipo', 'codigo_cie10', 'fecha_registro']
    list_filter = ['tipo', 'fecha_registro']
    search_fields = ['nombre', 'codigo_cie10', 'consulta__paciente__nombre']
    readonly_fields = ['fecha_registro']


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre_comercial', 'nombre_generico', 'categoria', 'presentacion', 'concentracion', 'activo']
    list_filter = ['categoria', 'activo', 'presentacion']
    search_fields = ['nombre_comercial', 'nombre_generico', 'categoria']
    readonly_fields = ['fecha_registro']


@admin.register(Prescripcion)
class PrescripcionAdmin(admin.ModelAdmin):
    list_display = ['medicamento', 'consulta', 'dosis', 'frecuencia', 'fecha_inicio', 'fecha_fin', 'activa']
    list_filter = ['frecuencia', 'via_administracion', 'activa', 'fecha_inicio']
    search_fields = ['medicamento__nombre_comercial', 'medicamento__nombre_generico', 'consulta__paciente__nombre']
    readonly_fields = ['fecha_registro']
    date_hierarchy = 'fecha_inicio'


@admin.register(ConversacionIA)
class ConversacionIAAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'titulo', 'fecha_inicio', 'requiere_atencion_medica', 'nivel_urgencia', 'activa']
    list_filter = ['requiere_atencion_medica', 'activa', 'fecha_inicio']
    search_fields = ['paciente__nombre', 'paciente__apellido_paterno', 'titulo', 'sintomas_mencionados']
    readonly_fields = ['fecha_inicio', 'fecha_ultima_actividad']
    date_hierarchy = 'fecha_inicio'


@admin.register(MensajeIA)
class MensajeIAAdmin(admin.ModelAdmin):
    list_display = ['conversacion', 'rol', 'fecha_envio', 'contenido_corto', 'contiene_sintomas', 'contiene_urgencia']
    list_filter = ['rol', 'contiene_sintomas', 'contiene_urgencia', 'fecha_envio']
    search_fields = ['conversacion__paciente__nombre', 'contenido']
    readonly_fields = ['fecha_envio']
    date_hierarchy = 'fecha_envio'
    
    def contenido_corto(self, obj):
        return obj.contenido[:100] + '...' if len(obj.contenido) > 100 else obj.contenido
    contenido_corto.short_description = 'Contenido'


@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'paciente', 'tipo', 'fecha_subida', 'tamanio_mb']
    list_filter = ['tipo', 'fecha_subida']
    search_fields = ['nombre', 'paciente__nombre', 'paciente__apellido_paterno', 'descripcion']
    readonly_fields = ['fecha_subida', 'tamanio']
    date_hierarchy = 'fecha_subida'
    
    def tamanio_mb(self, obj):
        return f"{obj.tamanio / (1024 * 1024):.2f} MB"
    tamanio_mb.short_description = 'Tamaño'


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo_display', 'especialidad', 'cedula_profesional', 'anos_experiencia', 'activo', 'acepta_nuevos_pacientes']
    list_filter = ['especialidad', 'activo', 'acepta_nuevos_pacientes', 'fecha_registro']
    search_fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'especialidad', 'cedula_profesional']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido_paterno', 'apellido_materno', 'sexo', 'fecha_nacimiento')
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'email', 'direccion')
        }),
        ('Información Profesional', {
            'fields': ('especialidad', 'sub_especialidad', 'cedula_profesional', 'cedula_especialidad', 
                      'universidad', 'anos_experiencia', 'biografia')
        }),
        ('Disponibilidad', {
            'fields': ('activo', 'acepta_nuevos_pacientes')
        }),
        ('Configuración de Consultas', {
            'fields': ('duracion_consulta_minutos', 'costo_consulta')
        }),
        ('Metadatos', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_completo_display(self, obj):
        return obj.nombre_completo()
    nombre_completo_display.short_description = 'Médico'


class HorarioMedicoInline(admin.TabularInline):
    model = HorarioMedico
    extra = 1
    fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']


@admin.register(HorarioMedico)
class HorarioMedicoAdmin(admin.ModelAdmin):
    list_display = ['medico', 'dia_semana_display', 'hora_inicio', 'hora_fin', 'activo']
    list_filter = ['dia_semana', 'activo', 'medico']
    search_fields = ['medico__nombre', 'medico__apellido_paterno']
    
    def dia_semana_display(self, obj):
        return obj.get_dia_semana_display()
    dia_semana_display.short_description = 'Día'


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'fecha', 'hora', 'estado']
    list_filter = ['estado', 'fecha', 'medico']
    search_fields = ['paciente__nombre', 'paciente__apellido_paterno', 'medico__nombre', 'medico__apellido_paterno', 'motivo']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('paciente', 'medico', 'fecha', 'hora', 'consultorio')
        }),
        ('Detalles de la Cita', {
            'fields': ('motivo', 'sintomas_iniciales')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Resultados de la Consulta', {
            'fields': ('diagnostico', 'tratamiento', 'observaciones'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_completada', 'cancelar_citas']
    
    def marcar_como_completada(self, request, queryset):
        updated = queryset.filter(estado='AGENDADA').update(estado='COMPLETADA')
        self.message_user(request, f'{updated} cita(s) marcada(s) como completada(s).')
    marcar_como_completada.short_description = 'Marcar como completada'
    
    def cancelar_citas(self, request, queryset):
        updated = queryset.filter(estado='AGENDADA').update(estado='CANCELADA')
        self.message_user(request, f'{updated} cita(s) cancelada(s).')
    cancelar_citas.short_description = 'Cancelar citas seleccionadas'

