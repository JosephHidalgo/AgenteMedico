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

const CitasAnteriores = () => {
  const [citasAnteriores, setCitasAnteriores] = useState<Cita[]>([]);
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
        const anteriores: Cita[] = [];

        todasCitasData.citas.forEach((cita) => {
          if (citaYaPaso(cita.fecha, cita.hora)) {
            anteriores.push(cita);
          }
        });

        anteriores.sort((a, b) => {
          const fechaA = new Date(`${a.fecha}T${a.hora}`);
          const fechaB = new Date(`${b.fecha}T${b.hora}`);
          return fechaB.getTime() - fechaA.getTime();
        });

        setCitasAnteriores(anteriores);
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
                <Calendar className="h-8 w-8 text-[#5fa7c1]" />
                Citas Anteriores
              </h1>
              <p className="text-muted-foreground mt-1">
                {cargando ? "Cargando..." : `${citasAnteriores.length} cita${citasAnteriores.length !== 1 ? 's' : ''} pasada${citasAnteriores.length !== 1 ? 's' : ''}`}
              </p>
            </div>
          </div>
        </div>

        {/* Lista de Citas */}
        {cargando ? (
          <div className="w-full text-center py-12">
            <p className="text-muted-foreground">Cargando citas...</p>
          </div>
        ) : citasAnteriores.length === 0 ? (
          <div className="w-full flex items-center justify-center py-12 px-4">
            <div className="max-w-2xl flex items-center gap-6">
              <div className="flex-shrink-0 w-16 h-16 rounded-full bg-[#5fa7c1]/10 flex items-center justify-center border border-[#5fa7c1]/20">
                <Calendar className="h-8 w-8 text-[#5fa7c1]" />
              </div>
              <div className="flex-1 text-left space-y-2">
                <h3 className="text-lg font-semibold text-foreground">
                  No hay citas anteriores
                </h3>
                <p className="text-sm text-muted-foreground">
                  Aquí aparecerán tus citas pasadas una vez que se completen
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {citasAnteriores.map((cita) => (
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

export default CitasAnteriores;
