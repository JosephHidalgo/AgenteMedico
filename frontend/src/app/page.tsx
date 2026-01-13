'use client';

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import VirtualAssistant from "@/components/VirtualAssistant";
import HealthCard from "@/components/HealthCard";
import AppointmentCard from "@/components/AppointmentCard";
import { Calendar, Users, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSidebar } from "@/components/ui/sidebar";
import Link from "next/link";
import { 
  estadisticasService, 
  citasService, 
  formatearFecha, 
  formatearHora,
  obtenerFechaHoy,
  type Cita 
} from "@/lib/api";

const Index = () => {
  // Hook del sidebar
  const { state: sidebarState } = useSidebar();
  const isSidebarCollapsed = sidebarState === "collapsed";
  
  // Estado para estadísticas
  const [estadisticas, setEstadisticas] = useState({
    total_citas: 0,
    total_pacientes: 0
  });

  // Estado para citas
  const [citasProximas, setCitasProximas] = useState<Cita[]>([]);
  const [citasAnteriores, setCitasAnteriores] = useState<Cita[]>([]);

  // Estado de carga
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    cargarDatos();
  }, []);

  /**
   * Verifica si una cita ya pasó (fecha y hora anteriores al momento actual)
   */
  const citaYaPaso = (fecha: string, hora: string): boolean => {
    const ahora = new Date();
    const [year, month, day] = fecha.split('-').map(Number);
    const [hours, minutes] = hora.split(':').map(Number);
    
    const fechaCita = new Date(year, month - 1, day, hours, minutes);
    
    return fechaCita < ahora;
  };

  /**
   * Verifica si una cita es para hoy
   */
  const esHoy = (fecha: string): boolean => {
    const hoy = obtenerFechaHoy();
    return fecha === hoy;
  };

  const cargarDatos = async () => {
    try {
      setCargando(true);

      // 1. Cargar TODAS las citas para obtener el total
      const todasCitasData = await citasService.listar({});

      if (todasCitasData.exito) {
        // Separar citas en próximas y anteriores
        const proximas: Cita[] = [];
        const anteriores: Cita[] = [];

        todasCitasData.citas.forEach((cita) => {
          if (citaYaPaso(cita.fecha, cita.hora)) {
            anteriores.push(cita);
          } else {
            proximas.push(cita);
          }
        });

        // Ordenar próximas
        proximas.sort((a, b) => {
          const fechaA = new Date(`${a.fecha}T${a.hora}`);
          const fechaB = new Date(`${b.fecha}T${b.hora}`);
          return fechaA.getTime() - fechaB.getTime();
        });

        // Ordenar anteriores
        anteriores.sort((a, b) => {
          const fechaA = new Date(`${a.fecha}T${a.hora}`);
          const fechaB = new Date(`${b.fecha}T${b.hora}`);
          return fechaB.getTime() - fechaA.getTime();
        });

        setCitasProximas(proximas);
        setCitasAnteriores(anteriores);
      }

      // 2. Cargar estadísticas
      const statsData = await estadisticasService.obtener();
      if (statsData.exito && todasCitasData.exito) {
        setEstadisticas({
          total_citas: todasCitasData.citas.length,
          total_pacientes: statsData.total_pacientes
        });
      }

    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setCargando(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 w-full overflow-x-hidden box-border">
        {/* Header Section with Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 w-full">
          {/* Title Section */}
          <div className="lg:col-span-1">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              ¡Bienvenido!
            </h1>
            <p className="text-base text-muted-foreground mb-3">
              Agenda tu cita médica de forma rápida y sencilla
            </p>
            <Link href="/nueva-cita">
              <Button size="default" className="gap-2">
                Agendar una cita
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          {/* Statistics Cards */}
          <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <HealthCard
              title="Total de Citas"
              icon={Calendar}
              value={cargando ? "..." : estadisticas.total_citas.toString()}
              subtitle="Citas registradas"
              iconClassName="bg-[#79b236]/10 text-[#79b236] border border-[#79b236]/20"
            />
            <HealthCard
              title="Total de Pacientes"
              icon={Users}
              value={cargando ? "..." : estadisticas.total_pacientes.toString()}
              subtitle="Pacientes registrados"
              iconClassName="bg-[#5fa7c1]/10 text-[#5fa7c1] border border-[#5fa7c1]/20"
            />
          </div>
        </div>

        {/* Próximas Citas - Marquee */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Calendar className="h-6 w-6 text-[#79b236]" />
              Próximas Citas
            </h2>
            <Link href="/citas-proximas">
              <Button variant="ghost" size="sm" className="gap-2">
                Ver todas las citas
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          
          {cargando ? (
            <div className="w-full text-center py-8">
              <p className="text-muted-foreground">Cargando citas...</p>
            </div>
          ) : citasProximas.length === 0 ? (
            <div className="w-full flex items-center justify-center py-6 px-4">
              <div className="max-w-2xl flex items-center gap-6">
                <div className="flex-shrink-0 w-16 h-16 rounded-full bg-[#79b236]/10 flex items-center justify-center border border-[#79b236]/20">
                  <Calendar className="h-8 w-8 text-[#79b236]" />
                </div>
                <div className="flex-1 text-left space-y-2">
                  <h3 className="text-lg font-semibold text-foreground">
                    No hay citas próximas
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Sé el primero en agendar una cita médica
                  </p>
                  <Link href="/nueva-cita">
                    <Button className="gap-2 mt-3">
                      Agendar cita
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          ) : (
            <div className={`mx-auto overflow-hidden ${isSidebarCollapsed ? 'max-w-[1400px]' : 'max-w-[1200px]'}`}>
              <div className="marquee-container">
                <div className={citasProximas.length > 4 ? "marquee-content" : "flex gap-4 justify-center"}>
                {citasProximas.map((cita) => (
                  <div key={cita.id} className="flex-shrink-0 w-[280px]">
                    <AppointmentCard
                      doctor={cita.medico_nombre}
                      specialty={cita.medico_especialidad}
                      patient={cita.paciente_nombre}
                      date={formatearFecha(cita.fecha)}
                      time={formatearHora(cita.hora)}
                      location={cita.consultorio}
                      status={cita.estado}
                      isToday={esHoy(cita.fecha)}
                    />
                  </div>
                ))}
                {/* Duplicar las cards para efecto infinito solo si hay más de 4 */}
                {citasProximas.length > 4 && citasProximas.map((cita) => (
                  <div key={`duplicate-${cita.id}`} className="flex-shrink-0 w-[280px]">
                    <AppointmentCard
                      doctor={cita.medico_nombre}
                      specialty={cita.medico_especialidad}
                      patient={cita.paciente_nombre}
                      date={formatearFecha(cita.fecha)}
                      time={formatearHora(cita.hora)}
                      location={cita.consultorio}
                      status={cita.estado}
                      isToday={esHoy(cita.fecha)}
                    />
                  </div>
                ))}
              </div>
              </div>
            </div>
          )}
        </div>

        {/* Citas Anteriores - Marquee */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Calendar className="h-6 w-6 text-[#5fa7c1]" />
              Citas Anteriores
            </h2>
            <Link href="/citas-anteriores">
              <Button variant="ghost" size="sm" className="gap-2">
                Ver todas las citas
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          
          {cargando ? (
            <div className="w-full text-center py-8">
              <p className="text-muted-foreground">Cargando citas...</p>
            </div>
          ) : citasAnteriores.length === 0 ? (
            <div className="w-full text-center py-8">
              <p className="text-muted-foreground">No hay citas anteriores</p>
            </div>
          ) : (
            <div className={`mx-auto overflow-hidden ${isSidebarCollapsed ? 'max-w-[1400px]' : 'max-w-[1200px]'}`}>
              <div className="marquee-container">
                <div className={citasAnteriores.length > 4 ? "marquee-content" : "flex gap-4 justify-center"} style={citasAnteriores.length > 4 ? { animationDuration: '70s' } : {}}>
                {citasAnteriores.map((cita) => (
                  <div key={cita.id} className="flex-shrink-0 w-[280px]">
                    <AppointmentCard
                      doctor={cita.medico_nombre}
                      specialty={cita.medico_especialidad}
                      patient={cita.paciente_nombre}
                      date={formatearFecha(cita.fecha)}
                      time={formatearHora(cita.hora)}
                      location={cita.consultorio}
                      status={cita.estado}
                      isToday={false}
                    />
                  </div>
                ))}
                {/* Duplicar las cards para efecto infinito solo si hay más de 4 */}
                {citasAnteriores.length > 4 && citasAnteriores.map((cita) => (
                  <div key={`duplicate-${cita.id}`} className="flex-shrink-0 w-[280px]">
                    <AppointmentCard
                      doctor={cita.medico_nombre}
                      specialty={cita.medico_especialidad}
                      patient={cita.paciente_nombre}
                      date={formatearFecha(cita.fecha)}
                      time={formatearHora(cita.hora)}
                      location={cita.consultorio}
                      status={cita.estado}
                      isToday={false}
                    />
                  </div>
                ))}
              </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Virtual Assistant */}
      <VirtualAssistant />
    </DashboardLayout>
  );
};

export default Index;
