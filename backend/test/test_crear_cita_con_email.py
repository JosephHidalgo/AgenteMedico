"""
Script para probar la creación completa de una cita con envío de email
Ejecutar con: python manage.py shell < test_crear_cita_con_email.py
"""

print("=" * 70)
print("PRUEBA COMPLETA: CREAR CITA + ENVIAR EMAIL")
print("=" * 70)

from datetime import date, time, timedelta
from medical.services.cita_service import CitaService
from medical.models import Medico

# Datos del paciente de prueba
datos_paciente = {
    'nombre': 'María',
    'apellido_paterno': 'González',
    'apellido_materno': 'López',
    'fecha_nacimiento': date(1990, 5, 15),
    'sexo': 'F',
    'email': 'hidalgoneirahenry@gmail.com',  # Usa tu email para recibir el correo
    'telefono': '5551234567'
}

# Obtener un médico disponible
try:
    medico = Medico.objects.filter(activo=True).first()
    
    if not medico:
        print("❌ No hay médicos activos en el sistema")
        print("   Ejecuta: python manage.py load_sample_data")
    else:
        print(f"\n📋 Datos de la cita:")
        print(f"   Paciente: {datos_paciente['nombre']} {datos_paciente['apellido_paterno']}")
        print(f"   Email: {datos_paciente['email']}")
        print(f"   Médico: Dr(a). {medico.nombre} {medico.apellido_paterno}")
        print(f"   Especialidad: {medico.especialidad}")
        
        # Datos de la cita (mañana a las 10:00 AM)
        fecha_cita = date.today() + timedelta(days=1)
        hora_cita = time(10, 0)
        
        datos_cita = {
            'medico_id': medico.id,
            'fecha': fecha_cita,
            'hora': hora_cita,
            'motivo': 'Consulta de prueba para validar sistema de emails',
            'sintomas_iniciales': 'Prueba del sistema automático de confirmación'
        }
        
        print(f"   Fecha: {fecha_cita.strftime('%d/%m/%Y')}")
        print(f"   Hora: {hora_cita.strftime('%H:%M')}")
        print(f"   Motivo: {datos_cita['motivo']}")
        
        print("\n🚀 Creando cita y enviando email...")
        print("-" * 70)
        
        # Crear la cita (esto automáticamente envía el email)
        try:
            cita, creada, mensaje = CitaService.crear_cita(datos_paciente, datos_cita)
            
            print(f"\n✅ {mensaje}")
            print(f"   Cita ID: {cita.id}")
            print(f"   Paciente ID: {cita.paciente.id}")
            print(f"   Estado: {cita.estado}")
            
            if "Email de confirmación enviado" in mensaje:
                print(f"\n📧 ¡EMAIL ENVIADO EXITOSAMENTE!")
                print(f"   Revisa el inbox de: {cita.paciente.email}")
                print(f"   Busca el asunto: ✓ Confirmación de Cita Médica - {fecha_cita.strftime('%d/%m/%Y')}")
            elif "problema al enviar el email" in mensaje:
                print(f"\n⚠️  La cita se creó pero hubo un problema con el email")
                print(f"   Revisa los logs del servidor para más detalles")
            
        except ValueError as e:
            print(f"\n❌ Error al crear la cita: {str(e)}")
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("NOTA: Revisa también la consola del servidor (runserver) para ver los logs")
print("=" * 70)
