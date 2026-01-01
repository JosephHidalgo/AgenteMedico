"""
Script de prueba para el servicio de email con Resend
Ejecutar con: python manage.py shell < test_email.py
"""

print("=" * 60)
print("PRUEBA DEL SERVICIO DE EMAIL CON RESEND")
print("=" * 60)

from medical.models import Cita
from medical.services.email_service import EmailService

# Obtener una cita de prueba (la más reciente)
try:
    cita = Cita.objects.filter(estado='AGENDADA').order_by('-id').first()
    
    if not cita:
        print("❌ No hay citas agendadas para probar")
        print("   Crea una cita primero usando el asistente virtual")
    else:
        print(f"\n✅ Cita encontrada:")
        print(f"   ID: {cita.id}")
        print(f"   Paciente: {cita.paciente.nombre} {cita.paciente.apellido_paterno}")
        print(f"   Email: {cita.paciente.email}")
        print(f"   Médico: Dr(a). {cita.medico.nombre} {cita.medico.apellido_paterno}")
        print(f"   Fecha: {cita.fecha.strftime('%d/%m/%Y')}")
        print(f"   Hora: {cita.hora.strftime('%H:%M')}")
        
        print("\n🚀 Enviando email de confirmación...")
        
        email_service = EmailService()
        resultado = email_service.enviar_confirmacion_cita(cita)
        
        print(f"\n{'✅' if resultado['exito'] else '❌'} Resultado:")
        print(f"   {resultado['mensaje']}")
        
        if resultado['exito']:
            print(f"   Email ID: {resultado.get('email_id', 'N/A')}")
            print(f"\n📧 Revisa el inbox de: {cita.paciente.email}")
        else:
            print("\n💡 Verifica:")
            print("   - Que RESEND_API_KEY esté configurada en .env")
            print("   - Que RESEND_FROM_EMAIL esté verificado en Resend")
            print("   - Que el paquete 'resend' esté instalado: pip install resend")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
