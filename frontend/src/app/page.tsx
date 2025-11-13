'use client';

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import VirtualAssistant from "@/components/VirtualAssistant";
import HealthCard from "@/components/HealthCard";
import AppointmentCard from "@/components/AppointmentCard";
import { Activity, Calendar, Heart, Pill, TrendingUp, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  estadisticasService, 
  citasService, 
  formatearFecha, 
  formatearHora,
  obtenerFechaHoy,
  type Cita 
} from "@/lib/api";

const Index = () => {
  // Estado para estadísticas
  const [estadisticas, setEstadisticas] = useState({
    citas_hoy: 0,
    citas_semana: 0,
    total_pacientes: 0,
    doctores_activos: 0
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

      // 1. Cargar estadísticas
      const statsData = await estadisticasService.obtener();
      if (statsData.exito) {
        setEstadisticas({
          citas_hoy: statsData.citas_hoy,
          citas_semana: statsData.citas_semana,
          total_pacientes: statsData.total_pacientes,
          doctores_activos: statsData.doctores_activos
        });
      }

      // 2. Cargar TODAS las citas
      const todasCitasData = await citasService.listar({});

      if (todasCitasData.exito) {
        const ahora = new Date();
        
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

        // Tomar solo las primeras 5 de cada categoría
        setCitasProximas(proximas.slice(0, 5));
        setCitasAnteriores(anteriores.slice(0, 5));
      }

    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setCargando(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Welcome Section */}
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Sistema de Gestión de Citas Médicas
          </h1>
          <p className="text-muted-foreground">
            Visualiza las citas programadas y gestiona el calendario médico
          </p>
        </div>

        {/* Statistics Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <HealthCard
            title="Citas Hoy"
            icon={Calendar}
            value={cargando ? "..." : estadisticas.citas_hoy.toString()}
            subtitle="Citas programadas para hoy"
            iconClassName="bg-secondary/10 text-secondary"
          />
          <HealthCard
            title="Citas Esta Semana"
            icon={Activity}
            value={cargando ? "..." : estadisticas.citas_semana.toString()}
            subtitle="Próximos 7 días"
            iconClassName="bg-primary/10 text-primary"
          />
          <HealthCard
            title="Total de Pacientes"
            icon={Heart}
            value={cargando ? "..." : estadisticas.total_pacientes.toString()}
            subtitle="Pacientes registrados"
            iconClassName="bg-accent/10 text-accent"
          />
          <HealthCard
            title="Doctores Activos"
            icon={Pill}
            value={cargando ? "..." : estadisticas.doctores_activos.toString()}
            subtitle="Disponibles hoy"
            iconClassName="bg-destructive/10 text-destructive"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Próximas Citas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Próximas Citas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {cargando ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Cargando citas...
                </p>
              ) : citasProximas.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No hay citas próximas programadas
                </p>
              ) : (
                citasProximas.map((cita) => (
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
                ))
              )}
            </CardContent>
          </Card>

          {/* Citas Anteriores */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-secondary" />
                Citas Anteriores
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {cargando ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Cargando citas...
                </p>
              ) : citasAnteriores.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No hay citas anteriores
                </p>
              ) : (
                citasAnteriores.map((cita) => (
                  <AppointmentCard
                    key={cita.id}
                    doctor={cita.medico_nombre}
                    specialty={cita.medico_especialidad}
                    patient={cita.paciente_nombre}
                    date={formatearFecha(cita.fecha)}
                    time={formatearHora(cita.hora)}
                    location={cita.consultorio}
                    status={cita.estado}
                    isToday={false}
                  />
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Virtual Assistant */}
      <VirtualAssistant />
    </DashboardLayout>
  );
};

export default Index;
