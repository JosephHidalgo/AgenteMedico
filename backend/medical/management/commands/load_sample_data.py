from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
import random
from medical.models import Paciente, Medico, HorarioMedico, Cita


class Command(BaseCommand):
    help = 'Carga datos de ejemplo en la base de datos del sistema medico'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('CARGANDO DATOS DE EJEMPLO'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        # Limpiar datos existentes
        self.stdout.write('Limpiando datos existentes...')
        Cita.objects.all().delete()
        HorarioMedico.objects.all().delete()
        Medico.objects.all().delete()
        Paciente.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Datos limpiados\n'))

        # Crear pacientes
        self.stdout.write('Creando pacientes...')
        
        pacientes = []
        pacientes.append(Paciente.objects.create(
            nombre='Maria', apellido_paterno='Gonzalez', apellido_materno='Lopez',
            fecha_nacimiento=date(1985, 3, 15), sexo='F', tipo_sangre='O+',
            telefono='5551234567', email='maria.gonzalez@example.com',
            direccion='Calle Principal 123', alergias='Penicilina',
            enfermedades_cronicas='Diabetes tipo 2'
        ))
        
        pacientes.append(Paciente.objects.create(
            nombre='Juan', apellido_paterno='Martinez', apellido_materno='Hernandez',
            fecha_nacimiento=date(1990, 7, 22), sexo='M', tipo_sangre='A+',
            telefono='5559876543', email='juan.martinez@example.com',
            direccion='Avenida Reforma 456'
        ))
        
        pacientes.append(Paciente.objects.create(
            nombre='Ana', apellido_paterno='Rodriguez', apellido_materno='Sanchez',
            fecha_nacimiento=date(1978, 11, 8), sexo='F', tipo_sangre='B+',
            telefono='5552468135', email='ana.rodriguez@example.com',
            direccion='Colonia Centro 789', alergias='Polen, Aspirina',
            enfermedades_cronicas='Hipertension'
        ))
        
        self.stdout.write(self.style.SUCCESS(f'{len(pacientes)} pacientes creados\n'))

        # Crear medicos
        self.stdout.write('Creando medicos...')
        
        medicos = []
        
        medicos.append(Medico.objects.create(
            nombre='Carlos', apellido_paterno='Ramirez', apellido_materno='Torres',
            sexo='M', fecha_nacimiento=date(1975, 4, 12),
            telefono='5551112233', email='dr.ramirez@hospital.com',
            direccion='Consultorio Torre Medica',
            especialidad='Medicina Interna', sub_especialidad='Endocrinologia',
            cedula_profesional='1234567', cedula_especialidad='ESP1234567',
            universidad='UNAM', anos_experiencia=20,
            biografia='Especialista en diabetes y enfermedades endocrinologicas.',
            duracion_consulta_minutos=30, costo_consulta=800.00
        ))
        
        medicos.append(Medico.objects.create(
            nombre='Laura', apellido_paterno='Fernandez', apellido_materno='Ruiz',
            sexo='F', fecha_nacimiento=date(1980, 6, 18),
            telefono='5554445566', email='dra.fernandez@hospital.com',
            direccion='Consultorio Torre Medica',
            especialidad='Medicina General', sub_especialidad='',
            cedula_profesional='2345678', cedula_especialidad='ESP2345678',
            universidad='UNAM', anos_experiencia=15,
            biografia='Medica general con experiencia en atencion primaria.',
            duracion_consulta_minutos=30, costo_consulta=600.00
        ))
        
        medicos.append(Medico.objects.create(
            nombre='Roberto', apellido_paterno='Garcia', apellido_materno='Mendoza',
            sexo='M', fecha_nacimiento=date(1972, 9, 25),
            telefono='5557778899', email='dr.garcia@hospital.com',
            direccion='Consultorio Torre Medica',
            especialidad='Cardiología', sub_especialidad='',
            cedula_profesional='3456789', cedula_especialidad='ESP3456789',
            universidad='UNAM', anos_experiencia=18,
            biografia='Especialista en enfermedades cardiovasculares.',
            duracion_consulta_minutos=30, costo_consulta=1200.00
        ))
        
        medicos.append(Medico.objects.create(
            nombre='Patricia', apellido_paterno='Morales', apellido_materno='Silva',
            sexo='F', fecha_nacimiento=date(1983, 2, 14),
            telefono='5552223344', email='dra.morales@hospital.com',
            direccion='Consultorio Torre Medica',
            especialidad='Dermatología', sub_especialidad='Cosmetica',
            cedula_profesional='4567890', cedula_especialidad='ESP4567890',
            universidad='UNAM', anos_experiencia=12,
            biografia='Dermatologa especializada en tratamientos esteticos.',
            duracion_consulta_minutos=30, costo_consulta=900.00
        ))
        
        medicos.append(Medico.objects.create(
            nombre='Miguel', apellido_paterno='Torres', apellido_materno='Vargas',
            sexo='M', fecha_nacimiento=date(1985, 11, 5),
            telefono='5556667788', email='dr.torres@hospital.com',
            direccion='Consultorio Torre Medica',
            especialidad='Pediatría', sub_especialidad='',
            cedula_profesional='5678901', cedula_especialidad='ESP5678901',
            universidad='UNAM', anos_experiencia=10,
            biografia='Pediatra dedicado al cuidado de ninos.',
            duracion_consulta_minutos=30, costo_consulta=700.00
        ))
        
        medicos.append(Medico.objects.create(
            nombre='Sandra', apellido_paterno='Lopez', apellido_materno='Ortiz',
            sexo='F', fecha_nacimiento=date(1978, 7, 20),
            telefono='5558889900', email='dra.lopez@hospital.com',
            direccion='Consultorio Torre Medica',
            especialidad='Traumatología', sub_especialidad='Deportiva',
            cedula_profesional='6789012', cedula_especialidad='ESP6789012',
            universidad='UNAM', anos_experiencia=14,
            biografia='Traumatologa especializada en lesiones deportivas.',
            duracion_consulta_minutos=30, costo_consulta=1000.00
        ))
        
        medicos.append(Medico.objects.create(
            nombre='Andres', apellido_paterno='Jimenez', apellido_materno='Cruz',
            sexo='M', fecha_nacimiento=date(1976, 3, 30),
            telefono='5553334455', email='psi.jimenez@hospital.com',
            direccion='Consultorio Torre Medica',
            especialidad='Psicología', sub_especialidad='Clínica',
            cedula_profesional='7890123', cedula_especialidad='ESP7890123',
            universidad='UNAM', anos_experiencia=16,
            biografia='Psicologo clinico especializado en terapia cognitivo-conductual.',
            duracion_consulta_minutos=45, costo_consulta=850.00
        ))
        
        medicos.append(Medico.objects.create(
            nombre='Gabriela', apellido_paterno='Castro', apellido_materno='Reyes',
            sexo='F', fecha_nacimiento=date(1988, 12, 8),
            telefono='5559990011', email='dra.castro@hospital.com',
            direccion='Consultorio Torre Medica',
            especialidad='Medicina General', sub_especialidad='',
            cedula_profesional='8901234', cedula_especialidad='ESP8901234',
            universidad='UNAM', anos_experiencia=8,
            biografia='Medica general con enfoque en medicina preventiva.',
            duracion_consulta_minutos=30, costo_consulta=550.00
        ))
        
        self.stdout.write(self.style.SUCCESS(f'{len(medicos)} medicos creados\n'))

        # Crear horarios
        self.stdout.write('Creando horarios de medicos...')
        
        dias_semana = [0, 1, 2, 3, 4]  # Lunes a Viernes
        horarios_count = 0
        
        for medico in medicos:
            dias_trabajo = random.sample(dias_semana, random.randint(3, 5))
            
            for dia in dias_trabajo:
                HorarioMedico.objects.create(
                    medico=medico,
                    dia_semana=dia,
                    hora_inicio=time(9, 0),
                    hora_fin=time(17, 0),
                    activo=True
                )
                horarios_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'{horarios_count} horarios creados\n'))

        # Crear citas
        self.stdout.write('Creando citas de prueba...')
        
        hoy = date.today()
        
        fechas_pasadas = [
            hoy - timedelta(days=7),
            hoy - timedelta(days=3),
            hoy - timedelta(days=1),
        ]
        
        fechas_futuras = [
            hoy + timedelta(days=1),
            hoy + timedelta(days=3),
            hoy + timedelta(days=7),
        ]
        
        citas_creadas = 0
        consultorio_num = 1
        
        # Citas pasadas con estados aleatorios
        for i, fecha in enumerate(fechas_pasadas):
            paciente = pacientes[i % len(pacientes)]
            medico = medicos[i % len(medicos)]
            
            estado = random.choices(
                ['COMPLETADA', 'EXPIRADA', 'CANCELADA'],
                weights=[70, 25, 5],
                k=1
            )[0]
            
            Cita.objects.create(
                paciente=paciente,
                medico=medico,
                fecha=fecha,
                hora=time(10, 0),
                duracion_minutos=30,
                motivo='Consulta de seguimiento',
                sintomas_iniciales='Evaluacion general de salud',
                consultorio=f'Consultorio {consultorio_num}',
                estado=estado
            )
            citas_creadas += 1
            consultorio_num += 1
        
        # Citas futuras (AGENDADA)
        for i, fecha in enumerate(fechas_futuras):
            paciente = pacientes[i % len(pacientes)]
            medico = medicos[(i + 3) % len(medicos)]
            
            Cita.objects.create(
                paciente=paciente,
                medico=medico,
                fecha=fecha,
                hora=time(14, 0),
                duracion_minutos=30,
                motivo='Consulta general',
                sintomas_iniciales='',
                consultorio=f'Consultorio {consultorio_num}',
                estado='AGENDADA'
            )
            citas_creadas += 1
            consultorio_num += 1
        
        self.stdout.write(self.style.SUCCESS(f'{citas_creadas} citas creadas\n'))

        # Resumen final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('RESUMEN DE DATOS CREADOS'))
        self.stdout.write('='*60)
        self.stdout.write(f'Pacientes: {Paciente.objects.count()}')
        self.stdout.write(f'Medicos: {Medico.objects.count()}')
        self.stdout.write(f'Horarios: {HorarioMedico.objects.count()}')
        self.stdout.write(f'Citas: {Cita.objects.count()}')
        self.stdout.write(f'  - AGENDADA: {Cita.objects.filter(estado="AGENDADA").count()}')
        self.stdout.write(f'  - COMPLETADA: {Cita.objects.filter(estado="COMPLETADA").count()}')
        self.stdout.write(f'  - EXPIRADA: {Cita.objects.filter(estado="EXPIRADA").count()}')
        self.stdout.write(f'  - CANCELADA: {Cita.objects.filter(estado="CANCELADA").count()}')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('\nDatos de ejemplo cargados exitosamente!\n'))
