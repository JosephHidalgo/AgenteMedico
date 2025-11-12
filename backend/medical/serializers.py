# encoding: utf-8
"""
Serializers para la API REST del sistema médico
"""
from rest_framework import serializers
from .models import Paciente, Medico, HorarioMedico, Cita


class PacienteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Paciente"""
    edad = serializers.SerializerMethodField()
    
    class Meta:
        model = Paciente
        fields = [
            'id', 'nombre', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'edad', 'sexo', 'tipo_sangre',
            'telefono', 'email', 'direccion',
            'alergias', 'enfermedades_cronicas',
            'fecha_registro', 'activo'
        ]
        read_only_fields = ['id', 'fecha_registro', 'edad']
    
    def get_edad(self, obj):
        """Calcular edad del paciente"""
        return obj.edad()


class MedicoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Médico"""
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Medico
        fields = [
            'id', 'nombre', 'apellido_paterno', 'apellido_paterno',
            'nombre_completo', 'especialidad', 'sub_especialidad',
            'cedula_profesional', 'cedula_especialidad',
            'anos_experiencia', 'universidad', 'biografia',
            'telefono', 'email', 'direccion',
            'costo_consulta', 'duracion_consulta_minutos',
            'acepta_nuevos_pacientes', 'activo'
        ]
        read_only_fields = ['id']
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo del médico"""
        return obj.nombre_completo()


class CitaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar citas"""
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    medico_nombre = serializers.CharField(source='medico.nombre_completo', read_only=True)
    medico_especialidad = serializers.CharField(source='medico.especialidad', read_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'id', 'paciente', 'paciente_nombre',
            'medico', 'medico_nombre', 'medico_especialidad',
            'fecha', 'hora', 'consultorio', 'estado',
            'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro']


class CitaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de citas"""
    paciente = PacienteSerializer(read_only=True)
    medico = MedicoSerializer(read_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'id', 'paciente', 'medico',
            'fecha', 'hora', 'duracion_minutos', 'tipo_consulta',
            'consultorio', 'motivo', 'sintomas_iniciales', 'notas_paciente',
            'estado', 'confirmada_por_paciente', 'recordatorio_enviado',
            'fecha_cancelacion', 'motivo_cancelacion',
            'fecha_registro', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_registro', 'fecha_actualizacion', 'fecha_cancelacion']


class CitaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear citas"""
    # Datos del paciente para get_or_create
    paciente_nombre = serializers.CharField(write_only=True)
    paciente_apellido_paterno = serializers.CharField(write_only=True)
    paciente_apellido_materno = serializers.CharField(write_only=True)
    paciente_email = serializers.EmailField(write_only=True)
    paciente_telefono = serializers.CharField(write_only=True)
    paciente_fecha_nacimiento = serializers.DateField(write_only=True)
    paciente_sexo = serializers.ChoiceField(choices=['M', 'F'], write_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'medico', 'fecha', 'hora', 'motivo', 'sintomas_iniciales',
            'paciente_nombre', 'paciente_apellido_paterno', 'paciente_apellido_materno',
            'paciente_email', 'paciente_telefono', 'paciente_fecha_nacimiento', 'paciente_sexo'
        ]
    
    def validate(self, data):
        """Validar que no exista otra cita en el mismo horario"""
        medico = data.get('medico')
        fecha = data.get('fecha')
        hora = data.get('hora')
        
        # Verificar si ya existe una cita en ese horario
        if Cita.objects.filter(
            medico=medico,
            fecha=fecha,
            hora=hora,
            estado__in=['AGENDADA', 'COMPLETADA']
        ).exists():
            raise serializers.ValidationError({
                'hora': 'El médico ya tiene una cita agendada en ese horario.'
            })
        
        return data


class HorarioMedicoSerializer(serializers.ModelSerializer):
    """Serializer para horarios de médicos"""
    medico_nombre = serializers.CharField(source='medico.nombre_completo', read_only=True)
    
    class Meta:
        model = HorarioMedico
        fields = [
            'id', 'medico', 'medico_nombre',
            'dia_semana', 'hora_inicio', 'hora_fin', 'activo'
        ]
        read_only_fields = ['id']


class MensajeAsistenteSerializer(serializers.Serializer):
    """Serializer para mensajes del asistente virtual"""
    mensaje = serializers.CharField(required=True)
    conversacion_id = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        fields = ['mensaje', 'conversacion_id']


class RespuestaAsistenteSerializer(serializers.Serializer):
    """Serializer para respuestas del asistente virtual"""
    conversacion_id = serializers.UUIDField()
    respuesta = serializers.CharField()
    intencion = serializers.CharField(required=False, allow_null=True)
    especialidad_sugerida = serializers.CharField(required=False, allow_null=True)
    es_urgente = serializers.BooleanField(default=False)
    
    class Meta:
        fields = ['conversacion_id', 'respuesta', 'intencion', 'especialidad_sugerida', 'es_urgente']
