import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Consulta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField()),
                ('motivo_consulta', models.TextField(help_text='Razón principal de la consulta')),
                ('sintomas', models.TextField(blank=True, help_text='Síntomas reportados por el paciente')),
                ('presion_arterial_sistolica', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(250)])),
                ('presion_arterial_diastolica', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(150)])),
                ('frecuencia_cardiaca', models.IntegerField(blank=True, help_text='Latidos por minuto', null=True, validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(220)])),
                ('temperatura', models.DecimalField(blank=True, decimal_places=1, help_text='Temperatura corporal en °C', max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(35.0), django.core.validators.MaxValueValidator(42.0)])),
                ('peso', models.DecimalField(blank=True, decimal_places=2, help_text='Peso en kg', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(500.0)])),
                ('altura', models.DecimalField(blank=True, decimal_places=2, help_text='Altura en metros', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0.4), django.core.validators.MaxValueValidator(2.5)])),
                ('observaciones', models.TextField(blank=True, help_text='Observaciones del médico')),
                ('plan_tratamiento', models.TextField(blank=True, help_text='Plan de tratamiento recomendado')),
                ('estado', models.CharField(choices=[('programada', 'Programada'), ('en_curso', 'En Curso'), ('completada', 'Completada'), ('cancelada', 'Cancelada')], default='programada', max_length=20)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Consulta',
                'verbose_name_plural': 'Consultas',
                'ordering': ['-fecha_hora'],
            },
        ),
        migrations.CreateModel(
            name='Medicamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_comercial', models.CharField(max_length=200)),
                ('nombre_generico', models.CharField(max_length=200)),
                ('categoria', models.CharField(help_text='Categoría del medicamento (antibiótico, analgésico, etc.)', max_length=100)),
                ('presentacion', models.CharField(help_text='Presentación (tabletas, jarabe, inyectable, etc.)', max_length=100)),
                ('concentracion', models.CharField(help_text='Concentración (500mg, 10ml, etc.)', max_length=100)),
                ('descripcion', models.TextField(blank=True)),
                ('contraindicaciones', models.TextField(blank=True)),
                ('efectos_secundarios', models.TextField(blank=True)),
                ('activo', models.BooleanField(default=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Medicamento',
                'verbose_name_plural': 'Medicamentos',
                'ordering': ['nombre_generico'],
            },
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellido_paterno', models.CharField(max_length=100)),
                ('apellido_materno', models.CharField(blank=True, max_length=100)),
                ('fecha_nacimiento', models.DateField()),
                ('sexo', models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], max_length=1)),
                ('tipo_sangre', models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=3)),
                ('telefono', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('direccion', models.TextField(blank=True)),
                ('alergias', models.TextField(blank=True, help_text='Alergias conocidas del paciente')),
                ('enfermedades_cronicas', models.TextField(blank=True, help_text='Enfermedades crónicas o condiciones pre-existentes')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Paciente',
                'verbose_name_plural': 'Pacientes',
                'ordering': ['-fecha_registro'],
            },
        ),
        migrations.CreateModel(
            name='ConversacionIA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(help_text='Título o resumen de la conversación', max_length=200)),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True)),
                ('fecha_ultima_actividad', models.DateTimeField(auto_now=True)),
                ('activa', models.BooleanField(default=True)),
                ('sintomas_mencionados', models.TextField(blank=True, help_text='Síntomas que el paciente mencionó')),
                ('temas_discutidos', models.TextField(blank=True, help_text='Temas principales de la conversación')),
                ('requiere_atencion_medica', models.BooleanField(default=False, help_text='Si la IA determina que requiere atención médica urgente')),
                ('nivel_urgencia', models.IntegerField(blank=True, help_text='Nivel de urgencia de 1 a 10', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('consulta', models.ForeignKey(blank=True, help_text='Consulta asociada si la conversación deriva en una', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversaciones_ia', to='medical.consulta')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversaciones_ia', to='medical.paciente')),
            ],
            options={
                'verbose_name': 'Conversación IA',
                'verbose_name_plural': 'Conversaciones IA',
                'ordering': ['-fecha_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Diagnostico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('principal', 'Principal'), ('secundario', 'Secundario'), ('diferencial', 'Diferencial')], default='principal', max_length=20)),
                ('codigo_cie10', models.CharField(blank=True, help_text='Código CIE-10', max_length=10)),
                ('nombre', models.CharField(help_text='Nombre del diagnóstico', max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('notas', models.TextField(blank=True, help_text='Notas adicionales del médico')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('consulta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diagnosticos', to='medical.consulta')),
            ],
            options={
                'verbose_name': 'Diagnóstico',
                'verbose_name_plural': 'Diagnósticos',
                'ordering': ['tipo', '-fecha_registro'],
            },
        ),
        migrations.CreateModel(
            name='MensajeIA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(choices=[('paciente', 'Paciente'), ('asistente', 'Asistente IA'), ('sistema', 'Sistema')], max_length=20)),
                ('contenido', models.TextField()),
                ('fecha_envio', models.DateTimeField(auto_now_add=True)),
                ('tokens_utilizados', models.IntegerField(blank=True, help_text='Tokens utilizados por el modelo de IA', null=True)),
                ('modelo_ia', models.CharField(blank=True, help_text='Modelo de IA utilizado (ej: GPT-4, Claude, etc.)', max_length=100)),
                ('contiene_sintomas', models.BooleanField(default=False)),
                ('contiene_urgencia', models.BooleanField(default=False)),
                ('conversacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='medical.conversacionia')),
            ],
            options={
                'verbose_name': 'Mensaje IA',
                'verbose_name_plural': 'Mensajes IA',
                'ordering': ['fecha_envio'],
            },
        ),
        migrations.CreateModel(
            name='HistorialMedico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_evento', models.DateField()),
                ('tipo_evento', models.CharField(help_text='Tipo de evento médico (cirugía, hospitalización, etc.)', max_length=100)),
                ('descripcion', models.TextField()),
                ('institucion', models.CharField(blank=True, help_text='Institución donde ocurrió el evento', max_length=200)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiales', to='medical.paciente')),
            ],
            options={
                'verbose_name': 'Historial Médico',
                'verbose_name_plural': 'Historiales Médicos',
                'ordering': ['-fecha_evento'],
            },
        ),
        migrations.AddField(
            model_name='consulta',
            name='paciente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultas', to='medical.paciente'),
        ),
        migrations.CreateModel(
            name='Archivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('laboratorio', 'Resultado de Laboratorio'), ('imagen', 'Imagen Médica'), ('receta', 'Receta Médica'), ('estudio', 'Estudio Médico'), ('documento', 'Documento General'), ('otro', 'Otro')], max_length=20)),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('archivo', models.FileField(upload_to='archivos_medicos/%Y/%m/')),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('tamanio', models.IntegerField(help_text='Tamaño del archivo en bytes')),
                ('consulta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archivos', to='medical.consulta')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='archivos', to='medical.paciente')),
            ],
            options={
                'verbose_name': 'Archivo',
                'verbose_name_plural': 'Archivos',
                'ordering': ['-fecha_subida'],
            },
        ),
        migrations.CreateModel(
            name='Prescripcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosis', models.CharField(help_text='Dosis a administrar', max_length=100)),
                ('frecuencia', models.CharField(choices=[('cada_4h', 'Cada 4 horas'), ('cada_6h', 'Cada 6 horas'), ('cada_8h', 'Cada 8 horas'), ('cada_12h', 'Cada 12 horas'), ('cada_24h', 'Cada 24 horas'), ('segun_necesidad', 'Según necesidad')], max_length=20)),
                ('via_administracion', models.CharField(choices=[('oral', 'Oral'), ('sublingual', 'Sublingual'), ('topica', 'Tópica'), ('intravenosa', 'Intravenosa'), ('intramuscular', 'Intramuscular'), ('subcutanea', 'Subcutánea'), ('rectal', 'Rectal'), ('oftalmica', 'Oftálmica'), ('otica', 'Ótica'), ('nasal', 'Nasal')], max_length=20)),
                ('duracion_dias', models.IntegerField(help_text='Duración del tratamiento en días', validators=[django.core.validators.MinValueValidator(1)])),
                ('instrucciones', models.TextField(blank=True, help_text='Instrucciones especiales para el paciente')),
                ('antes_despues_comida', models.CharField(choices=[('antes', 'Antes de comer'), ('despues', 'Después de comer'), ('con', 'Con alimentos'), ('indistinto', 'Indistinto')], default='indistinto', max_length=20)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('activa', models.BooleanField(default=True)),
                ('consulta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescripciones', to='medical.consulta')),
                ('medicamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prescripciones', to='medical.medicamento')),
            ],
            options={
                'verbose_name': 'Prescripción',
                'verbose_name_plural': 'Prescripciones',
                'ordering': ['-fecha_inicio'],
            },
        ),
    ]
