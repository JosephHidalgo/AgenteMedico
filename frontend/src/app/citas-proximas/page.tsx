'use client';

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import AppointmentCard from "@/components/AppointmentCard";
import { Calendar, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { 
  citasService, 
  formatearFecha, 
  formatearHora,
  obtenerFechaHoy,
  type Cita 
} from "@/lib/api";

const CitasProximas = () => {
  const [citasProximas, setCitasProximas] = useState<Cita[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    cargarCitas();
  }, []);

  const citaYaPaso = (fecha: string, hora: string): boolean => {
    const ahora = new Date();
    const [year, month, day] = fecha.split('-').map(Number);
    const [hours, minutes] = hora.split(':').map(Number);
    
    const fechaCita = new Date(year, month - 1, day, hours, minutes);
    
    return fechaCita < ahora;
  };

  const esHoy = (fecha: string): boolean => {
    const hoy = obtenerFechaHoy();
    return fecha === hoy;
  };

  const cargarCitas = async () => {
    try {
      setCargando(true);
      const todasCitasData = await citasService.listar({});

      if (todasCitasData.exito) {
        const proximas: Cita[] = [];

        todasCitasData.citas.forEach((cita) => {
          if (!citaYaPaso(cita.fecha, cita.hora)) {
            proximas.push(cita);
          }
        });

        proximas.sort((a, b) => {
          const fechaA = new Date(`${a.fecha}T${a.hora}`);
          const fechaB = new Date(`${b.fecha}T${b.hora}`);
          return fechaA.getTime() - fechaB.getTime();
        });

        setCitasProximas(proximas);
      }
    } catch (error) {
      console.error('Error al cargar citas:', error);
    } finally {
      setCargando(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
                <Calendar className="h-8 w-8 text-[#79b236]" />
                Próximas Citas
              </h1>
              <p className="text-muted-foreground mt-1">
                {cargando ? "Cargando..." : `${citasProximas.length} cita${citasProximas.length !== 1 ? 's' : ''} programada${citasProximas.length !== 1 ? 's' : ''}`}
              </p>
            </div>
          </div>
        </div>

        {/* Lista de Citas */}
        {cargando ? (
          <div className="w-full text-center py-12">
            <p className="text-muted-foreground">Cargando citas...</p>
          </div>
        ) : citasProximas.length === 0 ? (
          <div className="w-full flex items-center justify-center py-12 px-4">
            <div className="max-w-2xl flex items-center gap-6">
              <div className="flex-shrink-0 w-16 h-16 rounded-full bg-[#79b236]/10 flex items-center justify-center border border-[#79b236]/20">
                <Calendar className="h-8 w-8 text-[#79b236]" />
              </div>
              <div className="flex-1 text-left space-y-2">
                <h3 className="text-lg font-semibold text-foreground">
                  No hay citas próximas
                </h3>
                <p className="text-sm text-muted-foreground">
                  Comienza agendando tu primera cita médica
                </p>
                <Link href="/nueva-cita">
                  <Button className="gap-2 mt-3">
                    Agendar cita
                    <Calendar className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {citasProximas.map((cita) => (
              <AppointmentCard
                key={cita.id}
                doctor={cita.medico_nombre}
                specialty={cita.medico_especialidad}
                patient={cita.paciente_nombre}
                date={formatearFecha(cita.fecha)}
                time={formatearHora(cita.hora)}
                location={cita.consultorio}
                status={cita.estado}
                isToday={esHoy(cita.fecha)}
              />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default CitasProximas;
