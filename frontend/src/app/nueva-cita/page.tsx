"use client";

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { asistenteService, MensajeChat } from '@/lib/api';
import { Bot, Send, Loader2, AlertCircle, CheckCircle2, Calendar, Clock, User, Stethoscope, MapPin, ArrowLeft, RotateCcw } from "lucide-react";

/**
 * Formatea el texto convirtiendo **texto** a <strong>texto</strong>
 * y los saltos de línea a <br />
 */
const formatearMensaje = (texto: string) => {
  // Reemplazar **texto** por <strong>texto</strong>
  const partes = texto.split(/(\*\*.*?\*\*)/g);
  
  return partes.map((parte, index) => {
    if (parte.startsWith('**') && parte.endsWith('**')) {
      // Remover los asteriscos y hacer negrita
      const textoNegrita = parte.slice(2, -2);
      return <strong key={index}>{textoNegrita}</strong>;
    }
    // Manejar saltos de línea
    const lineas = parte.split('\n');
    return lineas.map((linea, lineaIndex) => (
      <span key={`${index}-${lineaIndex}`}>
        {linea}
        {lineaIndex < lineas.length - 1 && <br />}
      </span>
    ));
  });
};

const AsistenteVirtualPage = () => {
  const router = useRouter();
  const [mensajes, setMensajes] = useState<MensajeChat[]>([]);
  const [inputMensaje, setInputMensaje] = useState('');
  const [conversacionId, setConversacionId] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const [iniciando, setIniciando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creandoCita, setCreandoCita] = useState(false);
  const [mostrarBotonCita, setMostrarBotonCita] = useState(false);
  const [modalConfirmacion, setModalConfirmacion] = useState(false);
  const [modalExito, setModalExito] = useState(false);
  const [datosCita, setDatosCita] = useState<any>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al último mensaje
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [mensajes]);

  useEffect(() => {
    iniciarConversacion();
  }, []);

  const iniciarConversacion = async () => {
    try {
      setIniciando(true);
      setError(null);
      const response = await asistenteService.iniciarConversacion();
      
      if (response.exito) {
        setConversacionId(response.conversacion_id);
        setMensajes([{
          role: 'assistant',
          content: response.mensaje,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (err) {
      console.error('Error al iniciar conversación:', err);
      setError('No se pudo conectar con el asistente virtual. Por favor, intenta de nuevo.');
    } finally {
      setIniciando(false);
    }
  };

  const enviarMensaje = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMensaje.trim() || !conversacionId) return;

    const mensajeUsuario: MensajeChat = {
      role: 'user',
      content: inputMensaje,
      timestamp: new Date().toISOString()
    };

    setMensajes(prev => [...prev, mensajeUsuario]);
    setInputMensaje('');
    setCargando(true);
    setError(null);

    try {
      const response = await asistenteService.enviarMensaje(conversacionId, inputMensaje);
      
      if (response.exito) {
        const mensajeAsistente: MensajeChat = {
          role: 'assistant',
          content: response.respuesta,
          timestamp: new Date().toISOString()
        };
        setMensajes(prev => [...prev, mensajeAsistente]);

        // Mostrar alerta si es urgente
        if (response.es_urgente) {
          setTimeout(() => {
            alert('⚠️ ATENCIÓN: Se han detectado síntomas que requieren atención médica inmediata. Por favor, acude a urgencias.');
          }, 500);
        }

        // Detectar si el asistente pidió todos los datos para mostrar diálogo de confirmación
        if (response.respuesta.toLowerCase().includes('haz clic en el botón') || 
            response.respuesta.toLowerCase().includes('crear cita ahora')) {
          setMostrarBotonCita(true);
        }
      }
    } catch (err) {
      console.error('Error al enviar mensaje:', err);
      setError('Error al enviar el mensaje. Por favor, intenta de nuevo.');
    } finally {
      setCargando(false);
    }
  };

  const confirmarCrearCita = () => {
    setModalConfirmacion(true);
  };

  const intentarCrearCita = async () => {
    setModalConfirmacion(false);
    
    if (!conversacionId || creandoCita) return;

    try {
      setCreandoCita(true);
      const resultado = await asistenteService.crearCita(conversacionId);

      if (resultado.exito) {
        setDatosCita(resultado);
        setModalExito(true);
        setMostrarBotonCita(false);
      } else {
        // Mostrar el error específico del backend
        const mensajeError: MensajeChat = {
          role: 'assistant',
          content: `⚠️ ${resultado.error}\n\nPor favor, proporcióname todos los datos necesarios para agendar tu cita.`,
          timestamp: new Date().toISOString()
        };
        setMensajes(prev => [...prev, mensajeError]);
      }
    } catch (err: any) {
      console.error('Error al crear cita:', err);
      const mensajeError: MensajeChat = {
        role: 'assistant',
        content: '❌ Hubo un error al intentar crear la cita. Por favor, asegúrate de haber proporcionado todos tus datos (nombre completo, edad, email y teléfono).',
        timestamp: new Date().toISOString()
      };
      setMensajes(prev => [...prev, mensajeError]);
    } finally {
      setCreandoCita(false);
    }
  };

  const cerrarModalExito = () => {
    setModalExito(false);
    router.push('/');
  };

  const reiniciarConversacion = () => {
    setMensajes([]);
    setConversacionId(null);
    setError(null);
    setMostrarBotonCita(false);
    setDatosCita(null);
    iniciarConversacion();
  };

  const formatearHora = (timestamp: string | undefined) => {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-muted/30">
      {/* Header estilo WhatsApp */}
      <header className="bg-primary text-primary-foreground px-4 py-3 flex items-center gap-3 shadow-md flex-shrink-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push('/')}
          className="text-primary-foreground hover:bg-primary-foreground/10"
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="w-10 h-10 rounded-full bg-primary-foreground/20 flex items-center justify-center flex-shrink-0">
            <Bot className="w-6 h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="font-semibold text-base truncate">Asistente Virtual Médico</h1>
            <p className="text-xs text-primary-foreground/80">
              {iniciando ? 'Conectando...' : cargando ? 'Escribiendo...' : 'En línea'}
            </p>
          </div>
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={reiniciarConversacion}
          disabled={iniciando}
          className="text-primary-foreground hover:bg-primary-foreground/10 flex-shrink-0"
          title="Nueva conversación"
        >
          <RotateCcw className="w-5 h-5" />
        </Button>
      </header>

      {/* Área de mensajes - estilo WhatsApp */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto overflow-x-hidden px-3 sm:px-4 py-4"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      >
        {/* Estado de carga inicial */}
        {iniciando && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-3 bg-card p-6 rounded-xl shadow-sm">
              <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
              <p className="text-muted-foreground text-sm">Iniciando conversación...</p>
            </div>
          </div>
        )}

        {/* Error */}
        {error && !iniciando && (
          <div className="flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-lg max-w-md">
            <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
            <p className="text-destructive text-sm">{error}</p>
          </div>
        )}

        {/* Mensajes */}
        {!iniciando && (
          <div className="space-y-3">
            {mensajes.map((mensaje, index) => (
              <div
                key={index}
                className={`flex ${mensaje.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`relative max-w-[85%] sm:max-w-[75%] md:max-w-[65%] rounded-lg px-3 py-2 shadow-sm ${
                    mensaje.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-br-none'
                      : 'bg-card text-card-foreground rounded-bl-none'
                  }`}
                >
                  {/* Nombre del asistente */}
                  {mensaje.role === 'assistant' && (
                    <p className="text-xs font-semibold text-primary mb-1 flex items-center gap-1">
                      <Bot className="w-3 h-3" />
                      Asistente Virtual
                    </p>
                  )}
                  
                  {/* Contenido del mensaje con formato */}
                  <div className="text-sm leading-relaxed break-words">
                    {formatearMensaje(mensaje.content)}
                  </div>
                  
                  {/* Hora del mensaje */}
                  <p className={`text-[10px] mt-1 text-right ${
                    mensaje.role === 'user' 
                      ? 'text-primary-foreground/70' 
                      : 'text-muted-foreground'
                  }`}>
                    {formatearHora(mensaje.timestamp)}
                  </p>

                  {/* Pico del globo de chat */}
                  <div
                    className={`absolute bottom-0 w-3 h-3 ${
                      mensaje.role === 'user'
                        ? 'right-0 translate-x-1/2 bg-primary'
                        : 'left-0 -translate-x-1/2 bg-card'
                    }`}
                    style={{
                      clipPath: mensaje.role === 'user' 
                        ? 'polygon(0 0, 0 100%, 100% 100%)' 
                        : 'polygon(100% 0, 0 100%, 100% 100%)'
                    }}
                  />
                </div>
              </div>
            ))}

            {/* Indicador de escritura */}
            {cargando && (
              <div className="flex justify-start">
                <div className="bg-card rounded-lg px-4 py-3 shadow-sm rounded-bl-none relative">
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Área de input - estilo WhatsApp */}
      <div className="bg-muted/80 border-t border-border px-3 py-3 flex-shrink-0">
        {/* Botón crear cita si está disponible */}
        {mostrarBotonCita && (
          <div className="mb-2">
            <Button
              type="button"
              className="w-full bg-green-600 hover:bg-green-700 text-white"
              onClick={confirmarCrearCita}
              disabled={creandoCita}
            >
              {creandoCita ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Creando cita...
                </>
              ) : (
                <>
                  📅 Crear Cita Ahora
                </>
              )}
            </Button>
          </div>
        )}
        
        <form onSubmit={enviarMensaje} className="flex gap-2">
          <Input
            value={inputMensaje}
            onChange={(e) => setInputMensaje(e.target.value)}
            placeholder="Escribe un mensaje..."
            disabled={cargando || iniciando || !conversacionId}
            className="flex-1 rounded-full bg-card border-0 shadow-sm px-4 h-11"
            autoFocus
          />
          <Button
            type="submit"
            disabled={!inputMensaje.trim() || cargando || iniciando || !conversacionId}
            size="icon"
            className="rounded-full w-11 h-11 bg-primary hover:bg-primary/90 flex-shrink-0"
          >
            {cargando ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </form>
      </div>

      {/* Modal de Confirmación */}
      <Dialog open={modalConfirmacion} onOpenChange={setModalConfirmacion}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-primary" />
              Confirmar Cita Médica
            </DialogTitle>
            <DialogDescription>
              ¿Estás seguro de que deseas crear esta cita? Se asignará automáticamente un médico disponible y un horario apropiado.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setModalConfirmacion(false)}>
              Cancelar
            </Button>
            <Button onClick={intentarCrearCita} disabled={creandoCita}>
              {creandoCita ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Creando...
                </>
              ) : (
                'Confirmar'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Éxito */}
      <Dialog open={modalExito} onOpenChange={setModalExito}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="w-6 h-6" />
              ¡Cita Creada Exitosamente!
            </DialogTitle>
            <DialogDescription>
              Tu cita ha sido agendada correctamente. A continuación los detalles:
            </DialogDescription>
          </DialogHeader>
          
          {datosCita && (
            <div className="space-y-4 py-4">
              <div className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                <User className="w-5 h-5 text-primary mt-0.5" />
                <div>
                  <p className="text-xs text-muted-foreground">Paciente</p>
                  <p className="font-semibold text-foreground">{datosCita.paciente}</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-secondary/5 rounded-lg">
                <Stethoscope className="w-5 h-5 text-secondary mt-0.5" />
                <div>
                  <p className="text-xs text-muted-foreground">Médico</p>
                  <p className="font-semibold text-foreground">{datosCita.medico}</p>
                  <p className="text-sm text-muted-foreground">{datosCita.especialidad}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-start gap-2 p-3 bg-green-500/5 rounded-lg">
                  <Calendar className="w-5 h-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="text-xs text-muted-foreground">Fecha</p>
                    <p className="font-semibold text-sm text-foreground">
                      {new Date(datosCita.fecha).toLocaleDateString('es-ES', { 
                        day: 'numeric', 
                        month: 'long', 
                        year: 'numeric' 
                      })}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-2 p-3 bg-orange-500/5 rounded-lg">
                  <Clock className="w-5 h-5 text-orange-600 mt-0.5" />
                  <div>
                    <p className="text-xs text-muted-foreground">Hora</p>
                    <p className="font-semibold text-sm text-foreground">{datosCita.hora}</p>
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                <MapPin className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-xs text-muted-foreground">Consultorio</p>
                  <p className="font-semibold text-foreground">{datosCita.consultorio}</p>
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button onClick={cerrarModalExito} className="w-full">
              Ir al Inicio
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AsistenteVirtualPage;
