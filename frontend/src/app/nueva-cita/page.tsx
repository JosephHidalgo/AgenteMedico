"use client";

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { asistenteService, MensajeChat } from '@/lib/api';
import { Bot, Send, Loader2, AlertCircle, CheckCircle2, Calendar, Clock, User, Stethoscope, MapPin } from "lucide-react";

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

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
              <Bot className="w-8 h-8 text-blue-600" />
              Asistente Virtual Médico
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Evalúa tus síntomas o agenda una cita médica
            </p>
          </div>
          <Button
            onClick={reiniciarConversacion}
            variant="outline"
            disabled={iniciando}
          >
            Nueva Conversación
          </Button>
        </div>

        {/* Chat Container */}
        <Card className="flex flex-col" style={{ height: 'calc(100vh - 250px)' }}>
          <CardHeader className="border-b flex-shrink-0">
            <CardTitle className="text-lg flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              Asistente en línea
            </CardTitle>
          </CardHeader>
          
          <CardContent className="flex-1 p-4 flex flex-col overflow-hidden">
            {/* Área de mensajes con scroll */}
            <div className="flex-1 overflow-y-auto pr-2 mb-4" ref={scrollRef}>
              {iniciando && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center space-y-3">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
                    <p className="text-muted-foreground">Iniciando conversación...</p>
                  </div>
                </div>
              )}

              {error && (
                <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-red-600" />
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              <div className="space-y-4">
                {mensajes.map((mensaje, index) => (
                  <div
                    key={index}
                    className={`flex ${mensaje.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        mensaje.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-muted text-foreground'
                      }`}
                    >
                      {mensaje.role === 'assistant' && (
                        <div className="flex items-center gap-2 mb-2">
                          <Bot className="w-4 h-4" />
                          <span className="text-xs font-semibold">Asistente Virtual</span>
                        </div>
                      )}
                      <p className="text-sm whitespace-pre-wrap">{mensaje.content}</p>
                    </div>
                  </div>
                ))}

                {cargando && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-lg p-4 max-w-[80%]">
                      <div className="flex items-center gap-2">
                        <Bot className="w-4 h-4" />
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm text-muted-foreground">Escribiendo...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Input de mensaje */}
            <div className="border-t pt-4 flex-shrink-0">
              <form onSubmit={enviarMensaje} className="flex gap-2 mb-3">
                <Input
                  value={inputMensaje}
                  onChange={(e) => setInputMensaje(e.target.value)}
                  placeholder="Escribe tu mensaje aquí..."
                  disabled={cargando || iniciando || !conversacionId}
                  className="flex-1"
                  autoFocus
                />
                <Button
                  type="submit"
                  disabled={!inputMensaje.trim() || cargando || iniciando || !conversacionId}
                  size="icon"
                >
                  {cargando ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </form>
              
              {/* Botón para crear cita - solo cuando esté listo */}
              {mostrarBotonCita && (
                <Button
                  type="button"
                  variant="default"
                  className="w-full bg-green-600 hover:bg-green-700"
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
              )}
              
              <p className="text-xs text-muted-foreground text-center mt-2">
                💡 Puedes describir tus síntomas o solicitar agendar una cita médica
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Modal de Confirmación */}
        <Dialog open={modalConfirmacion} onOpenChange={setModalConfirmacion}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-blue-600" />
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
                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <User className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-xs text-muted-foreground">Paciente</p>
                    <p className="font-semibold text-foreground">{datosCita.paciente}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                  <Stethoscope className="w-5 h-5 text-purple-600 mt-0.5" />
                  <div>
                    <p className="text-xs text-muted-foreground">Médico</p>
                    <p className="font-semibold text-foreground">{datosCita.medico}</p>
                    <p className="text-sm text-muted-foreground">{datosCita.especialidad}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="flex items-start gap-2 p-3 bg-green-50 rounded-lg">
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

                  <div className="flex items-start gap-2 p-3 bg-orange-50 rounded-lg">
                    <Clock className="w-5 h-5 text-orange-600 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground">Hora</p>
                      <p className="font-semibold text-sm text-foreground">{datosCita.hora}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <MapPin className="w-5 h-5 text-gray-600 mt-0.5" />
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
    </DashboardLayout>
  );
};

export default AsistenteVirtualPage;
