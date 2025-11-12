"""
Management command para actualizar estados de citas pasadas
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from medical.models import Cita
import random


class Command(BaseCommand):
    help = 'Actualiza estados de citas AGENDADAS cuya fecha ya pasó, asignando aleatoriamente COMPLETADA, EXPIRADA o CANCELADA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué citas serían actualizadas sin modificar la base de datos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hoy = timezone.now().date()
        
        # Buscar solo citas AGENDADAS con fecha pasada
        citas_pasadas = Cita.objects.filter(
            estado='AGENDADA',
            fecha__lt=hoy
        )
        
        total_citas = citas_pasadas.count()
        
        if total_citas == 0:
            self.stdout.write(
                self.style.WARNING('No se encontraron citas AGENDADAS con fecha pasada')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n=== MODO DRY-RUN: No se modificará la base de datos ===\n')
            )
        
        # Contadores para estadísticas
        stats = {
            'COMPLETADA': 0,
            'EXPIRADA': 0,
            'CANCELADA': 0
        }
        
        for cita in citas_pasadas:
            # Asignar estado aleatorio con probabilidades:
            # 70% COMPLETADA, 25% EXPIRADA, 5% CANCELADA
            nuevo_estado = random.choices(
                ['COMPLETADA', 'EXPIRADA', 'CANCELADA'],
                weights=[70, 25, 5],
                k=1
            )[0]
            
            stats[nuevo_estado] += 1
            
            self.stdout.write(
                f"Cita #{cita.id} - {cita.paciente} con {cita.medico.nombre_completo()} "
                f"({cita.fecha}) → {nuevo_estado}"
            )
            
            if not dry_run:
                cita.estado = nuevo_estado
                cita.save(update_fields=['estado', 'fecha_actualizacion'])
        
        # Mostrar estadísticas
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'Total de citas procesadas: {total_citas}')
        self.stdout.write(f'  - COMPLETADA: {stats["COMPLETADA"]} ({stats["COMPLETADA"]/total_citas*100:.1f}%)')
        self.stdout.write(f'  - EXPIRADA: {stats["EXPIRADA"]} ({stats["EXPIRADA"]/total_citas*100:.1f}%)')
        self.stdout.write(f'  - CANCELADA: {stats["CANCELADA"]} ({stats["CANCELADA"]/total_citas*100:.1f}%)')
        self.stdout.write('='*60)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Ningún cambio fue guardado (modo dry-run)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {total_citas} citas actualizadas exitosamente')
            )
