"""
Servicio para envío de emails con PDF adjunto usando Resend
"""
import base64
import resend
from django.conf import settings
from .pdf_service import PDFService
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para enviar emails de confirmación de citas médicas
    con PDF adjunto usando Resend
    """
    
    def __init__(self):
        """Inicializa el servicio con la API key de Resend"""
        resend.api_key = settings.RESEND_API_KEY
    
    @staticmethod
    def generar_html_confirmacion(cita):
        """
        Genera el contenido HTML del email de confirmación
        
        Args:
            cita (Cita): Instancia del modelo Cita
            
        Returns:
            str: HTML del email
        """
        from datetime import datetime, time
        
        # Formatear datos
        fecha_formateada = cita.fecha.strftime('%d de %B de %Y')
        
        # Manejar hora como string o como objeto time
        if isinstance(cita.hora, str):
            # Si es string, convertir a objeto time primero
            try:
                hora_obj = datetime.strptime(cita.hora, '%H:%M:%S').time()
                hora_formateada = hora_obj.strftime('%I:%M %p')
            except:
                # Si no se puede convertir, usar el valor como está
                hora_formateada = cita.hora
        else:
            # Si ya es un objeto time
            hora_formateada = cita.hora.strftime('%I:%M %p')
        
        nombre_paciente = f"{cita.paciente.nombre} {cita.paciente.apellido_paterno}"
        nombre_medico = f"Dr(a). {cita.medico.nombre} {cita.medico.apellido_paterno}"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación de Cita Médica</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f6f9;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f6f9; padding: 40px 0;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; border-radius: 8px 8px 0 0; text-align: center;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">
                                        ✓ Cita Confirmada
                                    </h1>
                                </td>
                            </tr>
                            
                            <!-- Saludo -->
                            <tr>
                                <td style="padding: 30px 40px 20px;">
                                    <p style="margin: 0; font-size: 16px; color: #2c3e50; line-height: 1.6;">
                                        Estimado(a) <strong>{nombre_paciente}</strong>,
                                    </p>
                                    <p style="margin: 15px 0 0; font-size: 16px; color: #2c3e50; line-height: 1.6;">
                                        Su cita médica ha sido <strong style="color: #27ae60;">confirmada exitosamente</strong>. A continuación los detalles:
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Detalles de la Cita -->
                            <tr>
                                <td style="padding: 20px 40px;">
                                    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8f9fa; border-radius: 6px; border-left: 4px solid #667eea;">
                                        <tr>
                                            <td style="padding: 25px;">
                                                
                                                <!-- Médico -->
                                                <div style="margin-bottom: 20px;">
                                                    <p style="margin: 0; font-size: 13px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;">
                                                        👨‍⚕️ Médico
                                                    </p>
                                                    <p style="margin: 5px 0 0; font-size: 18px; color: #2c3e50; font-weight: 600;">
                                                        {nombre_medico}
                                                    </p>
                                                    <p style="margin: 3px 0 0; font-size: 14px; color: #7f8c8d;">
                                                        {cita.medico.especialidad}
                                                    </p>
                                                </div>
                                                
                                                <!-- Fecha y Hora -->
                                                <div style="margin-bottom: 20px;">
                                                    <p style="margin: 0; font-size: 13px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;">
                                                        📅 Fecha y Hora
                                                    </p>
                                                    <p style="margin: 5px 0 0; font-size: 18px; color: #2c3e50; font-weight: 600;">
                                                        {fecha_formateada}
                                                    </p>
                                                    <p style="margin: 3px 0 0; font-size: 16px; color: #667eea; font-weight: 600;">
                                                        {hora_formateada}
                                                    </p>
                                                </div>
                                                
                                                <!-- Consultorio -->
                                                <div style="margin-bottom: 0;">
                                                    <p style="margin: 0; font-size: 13px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;">
                                                        📍 Consultorio
                                                    </p>
                                                    <p style="margin: 5px 0 0; font-size: 16px; color: #2c3e50; font-weight: 500;">
                                                        {cita.consultorio}
                                                    </p>
                                                </div>
                                                
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            
                            <!-- Motivo -->
                            {f'''
                            <tr>
                                <td style="padding: 0 40px 20px;">
                                    <p style="margin: 0; font-size: 13px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;">
                                        📋 Motivo de la Consulta
                                    </p>
                                    <p style="margin: 8px 0 0; font-size: 15px; color: #2c3e50; line-height: 1.6;">
                                        {cita.motivo}
                                    </p>
                                </td>
                            </tr>
                            ''' if cita.motivo else ''}
                            
                            <!-- Instrucciones -->
                            <tr>
                                <td style="padding: 20px 40px;">
                                    <div style="background-color: #e8f4f8; border-left: 4px solid #3498db; padding: 20px; border-radius: 4px;">
                                        <p style="margin: 0; font-size: 14px; color: #2c3e50; line-height: 1.6;">
                                            <strong>📌 Instrucciones Importantes:</strong>
                                        </p>
                                        <ul style="margin: 10px 0 0; padding-left: 20px; font-size: 14px; color: #2c3e50; line-height: 1.8;">
                                            <li>Por favor, llegue <strong>15 minutos antes</strong> de su cita</li>
                                            <li>Traiga su identificación oficial y documentos médicos previos</li>
                                            <li>Adjuntamos un PDF con todos los detalles de su cita</li>
                                            <li>Si necesita cancelar o reprogramar, comuníquese con anticipación</li>
                                        </ul>
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; border-top: 1px solid #ecf0f1;">
                                    <p style="margin: 0; font-size: 14px; color: #7f8c8d; text-align: center; line-height: 1.6;">
                                        Si tiene alguna pregunta, no dude en contactarnos.
                                    </p>
                                    <p style="margin: 15px 0 0; font-size: 14px; color: #7f8c8d; text-align: center; line-height: 1.6;">
                                        <strong style="color: #2c3e50;">Sistema de Gestión Médica</strong><br>
                                        Este es un email automático, por favor no responder.
                                    </p>
                                </td>
                            </tr>
                            
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def enviar_confirmacion_cita(self, cita):
        """
        Envía un email de confirmación con PDF adjunto
        
        Args:
            cita (Cita): Instancia del modelo Cita
            
        Returns:
            dict: Resultado del envío
                {
                    'exito': bool,
                    'mensaje': str,
                    'email_id': str (si tuvo éxito)
                }
        """
        try:
            # Generar PDF
            pdf_buffer = PDFService.generar_pdf_cita(cita)
            pdf_content = pdf_buffer.getvalue()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            # Generar HTML del email
            html_content = self.generar_html_confirmacion(cita)
            
            # Preparar nombre del archivo PDF
            fecha_str = cita.fecha.strftime('%Y%m%d')
            nombre_archivo = f"Cita_Medica_{fecha_str}_{cita.id}.pdf"
            
            # Preparar datos del email
            email_data = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [cita.paciente.email],
                "subject": f"✓ Confirmación de Cita Médica - {cita.fecha.strftime('%d/%m/%Y')}",
                "html": html_content,
                "attachments": [
                    {
                        "filename": nombre_archivo,
                        "content": pdf_base64
                    }
                ]
            }
            
            # Enviar email con Resend
            response = resend.Emails.send(email_data)
            
            logger.info(f"Email enviado exitosamente a {cita.paciente.email}. ID: {response.get('id')}")
            
            return {
                'exito': True,
                'mensaje': f'Email enviado exitosamente a {cita.paciente.email}',
                'email_id': response.get('id')
            }
            
        except Exception as e:
            logger.error(f"Error al enviar email: {str(e)}")
            return {
                'exito': False,
                'mensaje': f'Error al enviar email: {str(e)}'
            }
    
    def enviar_email_personalizado(self, destinatario, asunto, html_content, adjuntos=None):
        """
        Envía un email personalizado
        
        Args:
            destinatario (str): Email del destinatario
            asunto (str): Asunto del email
            html_content (str): Contenido HTML del email
            adjuntos (list, optional): Lista de adjuntos en formato:
                [{"filename": "nombre.pdf", "content": "base64_content"}]
        
        Returns:
            dict: Resultado del envío
        """
        try:
            email_data = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [destinatario],
                "subject": asunto,
                "html": html_content
            }
            
            if adjuntos:
                email_data["attachments"] = adjuntos
            
            response = resend.Emails.send(email_data)
            
            return {
                'exito': True,
                'mensaje': f'Email enviado exitosamente a {destinatario}',
                'email_id': response.get('id')
            }
            
        except Exception as e:
            logger.error(f"Error al enviar email personalizado: {str(e)}")
            return {
                'exito': False,
                'mensaje': f'Error al enviar email: {str(e)}'
            }
