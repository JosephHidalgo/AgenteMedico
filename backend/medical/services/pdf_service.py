"""
Servicio para generación de PDFs de citas médicas
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime


class PDFService:
    """
    Servicio para generar PDFs profesionales de citas médicas
    """
    
    @staticmethod
    def generar_pdf_cita(cita):
        """
        Genera un PDF con los detalles de una cita médica
        
        Args:
            cita (Cita): Instancia del modelo Cita
        
        Returns:
            BytesIO: Buffer con el PDF generado
        """
        buffer = BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Contenedor para elementos del PDF
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para el título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulos
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6
        )
        
        # ====================
        # ENCABEZADO
        # ====================
        story.append(Paragraph("CONFIRMACIÓN DE CITA MÉDICA", titulo_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Estado de la cita con color
        estado_color = {
            'AGENDADA': colors.HexColor('#27ae60'),
            'COMPLETADA': colors.HexColor('#3498db'),
            'CANCELADA': colors.HexColor('#e74c3c'),
            'EXPIRADA': colors.HexColor('#95a5a6')
        }.get(cita.estado, colors.black)
        
        estado_style = ParagraphStyle(
            'EstadoStyle',
            parent=normal_style,
            fontSize=14,
            textColor=estado_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph(f"Estado: {cita.get_estado_display()}", estado_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # ====================
        # INFORMACIÓN DE LA CITA
        # ====================
        story.append(Paragraph("DETALLES DE LA CITA", subtitulo_style))
        
        # Tabla de información de la cita
        fecha_str = cita.fecha.strftime('%d de %B de %Y')
        hora_str = cita.hora.strftime('%H:%M')
        
        cita_data = [
            ['Fecha:', fecha_str],
            ['Hora:', hora_str],
            ['Duración:', f'{cita.duracion_minutos} minutos'],
            ['Consultorio:', cita.consultorio],
            ['Tipo:', cita.get_tipo_consulta_display()],
        ]
        
        cita_table = Table(cita_data, colWidths=[2*inch, 4*inch])
        cita_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(cita_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # ====================
        # INFORMACIÓN DEL MÉDICO
        # ====================
        story.append(Paragraph("MÉDICO TRATANTE", subtitulo_style))
        
        medico_data = [
            ['Nombre:', cita.medico.nombre_completo()],
            ['Especialidad:', cita.medico.especialidad],
        ]
        
        if cita.medico.sub_especialidad:
            medico_data.append(['Sub-especialidad:', cita.medico.sub_especialidad])
        
        medico_data.extend([
            ['Cédula Profesional:', cita.medico.cedula_profesional],
            ['Teléfono:', cita.medico.telefono],
            ['Email:', cita.medico.email],
        ])
        
        medico_table = Table(medico_data, colWidths=[2*inch, 4*inch])
        medico_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(medico_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # ====================
        # INFORMACIÓN DEL PACIENTE
        # ====================
        story.append(Paragraph("PACIENTE", subtitulo_style))
        
        paciente_data = [
            ['Nombre:', f"{cita.paciente.nombre} {cita.paciente.apellido_paterno}"],
            ['Edad:', f"{cita.paciente.edad()} años"],
            ['Email:', cita.paciente.email],
            ['Teléfono:', cita.paciente.telefono],
        ]
        
        paciente_table = Table(paciente_data, colWidths=[2*inch, 4*inch])
        paciente_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(paciente_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # ====================
        # MOTIVO DE LA CITA
        # ====================
        if cita.motivo:
            story.append(Paragraph("MOTIVO DE CONSULTA", subtitulo_style))
            story.append(Paragraph(cita.motivo, normal_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # ====================
        # SÍNTOMAS INICIALES
        # ====================
        if cita.sintomas_iniciales:
            story.append(Paragraph("SÍNTOMAS MENCIONADOS", subtitulo_style))
            story.append(Paragraph(cita.sintomas_iniciales, normal_style))
            story.append(Spacer(1, 0.3 * inch))
        
        # ====================
        # INSTRUCCIONES
        # ====================
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("INSTRUCCIONES", subtitulo_style))
        
        instrucciones = [
            "• Llegue 15 minutos antes de su cita",
            "• Traiga su identificación oficial",
            "• Traiga estudios médicos previos (si los tiene)",
            "• Si necesita cancelar, hágalo con al menos 24 horas de anticipación"
        ]
        
        for instruccion in instrucciones:
            story.append(Paragraph(instruccion, normal_style))
        
        # ====================
        # PIE DE PÁGINA
        # ====================
        story.append(Spacer(1, 0.5 * inch))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER
        )
        
        fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M')
        story.append(Paragraph(
            f"Documento generado el {fecha_generacion}",
            footer_style
        ))
        story.append(Paragraph(
            f"ID de Cita: {cita.id}",
            footer_style
        ))
        
        # Construir PDF
        doc.build(story)
        
        # Mover al inicio del buffer
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def obtener_nombre_archivo(cita):
        """
        Genera un nombre de archivo apropiado para el PDF de la cita
        
        Args:
            cita (Cita): Instancia del modelo Cita
        
        Returns:
            str: Nombre del archivo
        """
        fecha_str = cita.fecha.strftime('%Y%m%d')
        paciente_nombre = f"{cita.paciente.nombre}_{cita.paciente.apellido_paterno}"
        paciente_nombre = paciente_nombre.replace(' ', '_')
        
        return f"cita_{fecha_str}_{paciente_nombre}_{cita.id}.pdf"
