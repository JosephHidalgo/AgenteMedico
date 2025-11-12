from django.core.management.base import BaseCommand
from medical.services import AsistenteVirtualService
from medical.models import Paciente


class Command(BaseCommand):
    help = 'Prueba el asistente virtual con una conversación de ejemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--paciente-id',
            type=int,
            default=1,
            help='ID del paciente para la conversación de prueba'
        )

    def handle(self, *args, **options):
        paciente_id = options['paciente_id']
        
        try:
            paciente = Paciente.objects.get(id=paciente_id)
        except Paciente.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Paciente con ID {paciente_id} no encontrado'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'✅ Probando asistente con paciente: {paciente.nombre} {paciente.apellido_paterno}'))
        self.stdout.write('')
        
        # Crear el servicio
        asistente = AsistenteVirtualService()
        
        # Iniciar conversación
        self.stdout.write(self.style.WARNING('🤖 Iniciando conversación...'))
        conversacion = asistente.iniciar_conversacion(
            paciente_id=paciente_id,
            titulo='Prueba del Asistente Virtual'
        )
        
        # Obtener mensaje de bienvenida
        mensaje_bienvenida = conversacion.mensajes.filter(rol='asistente').first()
        if mensaje_bienvenida:
            self.stdout.write(self.style.SUCCESS(f'\n💬 Asistente: {mensaje_bienvenida.contenido}\n'))
        
        # Conversación de prueba
        mensajes_prueba = [
            "Hola, tengo dolor de cabeza desde ayer",
            "También tengo un poco de fiebre, como 37.8°C",
            "No, no tengo otros síntomas. Solo el dolor y la fiebre",
        ]
        
        for i, mensaje_texto in enumerate(mensajes_prueba, 1):
            self.stdout.write(self.style.WARNING(f'\n👤 Paciente: {mensaje_texto}'))
            
            # Enviar mensaje
            respuesta = asistente.enviar_mensaje(conversacion.id, mensaje_texto)
            
            if respuesta['exito']:
                self.stdout.write(self.style.SUCCESS(f'\n💬 Asistente: {respuesta["mensaje"]}\n'))
                
                # Mostrar análisis
                if respuesta.get('analisis'):
                    analisis = respuesta['analisis']
                    self.stdout.write(self.style.WARNING('📊 Análisis:'))
                    self.stdout.write(f'   - Contiene síntomas: {analisis["contiene_sintomas"]}')
                    self.stdout.write(f'   - Nivel de urgencia: {analisis.get("nivel_urgencia", "N/A")}')
                    if analisis['sintomas_detectados']:
                        self.stdout.write(f'   - Síntomas detectados: {", ".join(analisis["sintomas_detectados"])}')
                
                # Mostrar si requiere atención
                if respuesta.get('requiere_atencion'):
                    self.stdout.write(self.style.ERROR(f'\n⚠️  REQUIERE ATENCIÓN MÉDICA (Urgencia: {respuesta["nivel_urgencia"]})\n'))
                
                # Mostrar tokens usados
                if respuesta.get('tokens_usados'):
                    self.stdout.write(self.style.NOTICE(f'   💰 Tokens usados: {respuesta["tokens_usados"]}\n'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Error: {respuesta.get("error")}'))
                break
        
        # Finalizar conversación
        self.stdout.write(self.style.WARNING('\n🔚 Finalizando conversación...'))
        resultado = asistente.finalizar_conversacion(conversacion.id)
        
        if resultado['exito']:
            self.stdout.write(self.style.SUCCESS('✅ Conversación finalizada correctamente'))
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('📋 RESUMEN DE LA CONVERSACIÓN'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Conversación ID: {conversacion.id}')
        self.stdout.write(f'Paciente: {conversacion.paciente.nombre}')
        self.stdout.write(f'Total de mensajes: {conversacion.mensajes.count()}')
        self.stdout.write(f'Síntomas mencionados: {conversacion.sintomas_mencionados or "Ninguno"}')
        self.stdout.write(f'Requiere atención: {"Sí" if conversacion.requiere_atencion_medica else "No"}')
        if conversacion.nivel_urgencia:
            self.stdout.write(f'Nivel de urgencia: {conversacion.nivel_urgencia}/10')
        
        # Calcular tokens totales
        tokens_totales = sum(
            m.tokens_utilizados or 0 
            for m in conversacion.mensajes.filter(rol='asistente')
        )
        if tokens_totales:
            self.stdout.write(f'Tokens totales usados: {tokens_totales}')
            costo_estimado = (tokens_totales / 1000000) * 0.15  # Precio aproximado de gpt-4o-mini
            self.stdout.write(f'Costo estimado: ${costo_estimado:.4f} USD')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Prueba completada exitosamente!'))
        self.stdout.write(self.style.NOTICE('\n💡 Tip: Puedes ver la conversación en el admin de Django'))
        self.stdout.write(f'   http://localhost:8000/admin/medical/conversacionia/{conversacion.id}/change/')
