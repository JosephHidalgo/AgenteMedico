'use client';

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar as CalendarIcon, Clock, User, MapPin } from "lucide-react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import { citasService, formatearHora, type Cita } from "@/lib/api";

export default function CalendarioPage() {
  const [fechaSeleccionada, setFechaSeleccionada] = useState<Date>(new Date());
  const [citasDelMes, setCitasDelMes] = useState<Cita[]>([]);
  const [citasDelDia, setCitasDelDia] = useState<Cita[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    cargarCitasDelMes(fechaSeleccionada);
  }, [fechaSeleccionada]);

  const cargarCitasDelMes = async (fecha: Date) => {
    try {
      setCargando(true);
      
      // Obtener primer y último día del mes
      const primerDia = new Date(fecha.getFullYear(), fecha.getMonth(), 1);
      const ultimoDia = new Date(fecha.getFullYear(), fecha.getMonth() + 1, 0);
      
      const fechaDesde = primerDia.toISOString().split('T')[0];
      const fechaHasta = ultimoDia.toISOString().split('T')[0];
      
      const response = await citasService.listar({
        fecha_desde: fechaDesde,
        fecha_hasta: fechaHasta
      });
      
      if (response.exito) {
        setCitasDelMes(response.citas);
        // Filtrar citas del día seleccionado
        filtrarCitasDelDia(fecha, response.citas);
      }
    } catch (error) {
      console.error('Error al cargar citas:', error);
    } finally {
      setCargando(false);
    }
  };

  const filtrarCitasDelDia = (fecha: Date, citas: Cita[]) => {
    const fechaStr = fecha.toISOString().split('T')[0];
    const citasFiltradas = citas.filter(cita => cita.fecha === fechaStr);
    // Ordenar por hora
    citasFiltradas.sort((a, b) => a.hora.localeCompare(b.hora));
    setCitasDelDia(citasFiltradas);
  };

  const handleFechaChange = (value: any) => {
    setFechaSeleccionada(value);
    filtrarCitasDelDia(value, citasDelMes);
  };

  const tieneCitas = (fecha: Date): boolean => {
    const fechaStr = fecha.toISOString().split('T')[0];
    return citasDelMes.some(cita => cita.fecha === fechaStr);
  };

  const contarCitas = (fecha: Date): number => {
    const fechaStr = fecha.toISOString().split('T')[0];
    return citasDelMes.filter(cita => cita.fecha === fechaStr).length;
  };

  const getTileClassName = ({ date, view }: { date: Date; view: string }) => {
    if (view === 'month') {
      const fechaStr = date.toISOString().split('T')[0];
      const citasDelDia = citasDelMes.filter(cita => cita.fecha === fechaStr);
      
      if (citasDelDia.length > 0) {
        // Prioridad: Agendada > Completada > Cancelada
        const tieneAgendada = citasDelDia.some(c => c.estado === 'AGENDADA');
        const tieneCompletada = citasDelDia.some(c => c.estado === 'COMPLETADA');
        const tieneCancelada = citasDelDia.some(c => c.estado === 'CANCELADA');
        
        if (tieneAgendada) return 'cita-agendada';
        if (tieneCompletada) return 'cita-completada';
        if (tieneCancelada) return 'cita-cancelada';
      }
    }
    return '';
  };

  const getTileContent = ({ date, view }: { date: Date; view: string }) => {
    if (view === 'month' && tieneCitas(date)) {
      const cantidad = contarCitas(date);
      return (
        <div className="absolute top-1 right-1">
          <div className="h-5 w-5 rounded-full bg-background/80 backdrop-blur-sm flex items-center justify-center text-[10px] font-bold">
            {cantidad}
          </div>
        </div>
      );
    }
    return null;
  };

  const getEstadoBadge = (estado: string) => {
    const colores: Record<string, string> = {
      AGENDADA: "bg-[#79b236]/10 text-[#79b236] border border-[#79b236]/20",
      COMPLETADA: "bg-[#5fa7c1]/10 text-[#5fa7c1] border border-[#5fa7c1]/20",
      CANCELADA: "bg-red-500/10 text-red-700 dark:text-red-400 border border-red-500/20",
      EXPIRADA: "bg-gray-500/10 text-gray-700 dark:text-gray-400 border border-gray-500/20"
    };
    
    const labels: Record<string, string> = {
      AGENDADA: "Agendada",
      COMPLETADA: "Completada",
      CANCELADA: "Cancelada",
      EXPIRADA: "Expirada"
    };
    
    return (
      <Badge className={colores[estado] || colores.EXPIRADA}>
        {labels[estado] || estado}
      </Badge>
    );
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header con Estadísticas */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Calendario de Citas
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Visualiza todas las citas médicas programadas en el calendario
            </p>
          </div>

          {/* Estadísticas del Mes - Solo visible en pantallas grandes */}
          <div className="hidden lg:flex gap-6">
            <div className="text-center">
              <p className="text-xs text-muted-foreground">Total de Citas</p>
              <p className="text-2xl font-bold text-foreground">{citasDelMes.length}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground">Agendadas</p>
              <p className="text-2xl font-bold text-[#79b236]">
                {citasDelMes.filter(c => c.estado === 'AGENDADA').length}
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground">Completadas</p>
              <p className="text-2xl font-bold text-[#5fa7c1]">
                {citasDelMes.filter(c => c.estado === 'COMPLETADA').length}
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground">Canceladas</p>
              <p className="text-2xl font-bold text-red-600">
                {citasDelMes.filter(c => c.estado === 'CANCELADA').length}
              </p>
            </div>
          </div>
        </div>

        {/* Calendario y Detalles */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Calendario */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
                <CalendarIcon className="h-5 w-5 text-primary" />
                Calendario del Mes
              </CardTitle>
            </CardHeader>
            <CardContent className="px-2 sm:px-6">
              {cargando ? (
                <div className="flex items-center justify-center h-96">
                  <p className="text-muted-foreground">Cargando calendario...</p>
                </div>
              ) : (
                <div className="calendario-container">
                  <Calendar
                    onChange={handleFechaChange}
                    value={fechaSeleccionada}
                    locale="es-ES"
                    tileClassName={getTileClassName}
                    tileContent={getTileContent}
                    className="w-full border-none shadow-none"
                  />
                </div>
              )}
              
              {/* Leyenda */}
              <div className="mt-6 pt-4 border-t border-border">
                <p className="text-sm font-medium text-foreground mb-3">Leyenda:</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex items-center gap-2">
                    <div className="h-4 w-4 rounded bg-[#79b236]/20 border-2 border-[#79b236]"></div>
                    <span className="text-xs sm:text-sm text-muted-foreground">Agendada</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-4 w-4 rounded bg-[#5fa7c1]/20 border-2 border-[#5fa7c1]"></div>
                    <span className="text-xs sm:text-sm text-muted-foreground">Completada</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-4 w-4 rounded bg-red-500/20 border-2 border-red-500"></div>
                    <span className="text-xs sm:text-sm text-muted-foreground">Cancelada</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-4 w-4 rounded bg-primary/20 border-2 border-primary"></div>
                    <span className="text-xs sm:text-sm text-muted-foreground">Hoy</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Citas del Día Seleccionado */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
                <Clock className="h-5 w-5 text-secondary" />
                Citas del Día
              </CardTitle>
              <p className="text-xs sm:text-sm text-muted-foreground">
                {fechaSeleccionada.toLocaleDateString('es-ES', {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric'
                })}
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {citasDelDia.length === 0 ? (
                  <div className="text-center py-8">
                    <CalendarIcon className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground">
                      No hay citas programadas para este día
                    </p>
                  </div>
                ) : (
                  citasDelDia.map((cita) => (
                    <Card key={cita.id} className="p-3 sm:p-4 hover:shadow-md transition-shadow">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-1 min-w-0 flex-1">
                            <p className="font-semibold text-foreground text-sm sm:text-base truncate">
                              {cita.medico_nombre}
                            </p>
                            <p className="text-xs sm:text-sm text-muted-foreground truncate">
                              {cita.medico_especialidad}
                            </p>
                          </div>
                          <div className="flex-shrink-0">
                            {getEstadoBadge(cita.estado)}
                          </div>
                        </div>
                        
                        <div className="space-y-2 text-xs sm:text-sm">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <User className="h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
                            <span className="truncate">{cita.paciente_nombre}</span>
                          </div>
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Clock className="h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
                            <span>{formatearHora(cita.hora)}</span>
                          </div>
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <MapPin className="h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
                            <span className="truncate">{cita.consultorio}</span>
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}