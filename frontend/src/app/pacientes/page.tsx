"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Users, 
  Search, 
  Phone, 
  Mail, 
  Calendar, 
  Stethoscope,
  Loader2,
  AlertCircle,
  User
} from "lucide-react";
import { pacientesService, Paciente } from "@/lib/api";

const PacientesPage = () => {
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busqueda, setBusqueda] = useState("");
  const [busquedaActiva, setBusquedaActiva] = useState("");

  useEffect(() => {
    cargarPacientes();
  }, [busquedaActiva]);

  const cargarPacientes = async () => {
    try {
      setCargando(true);
      setError(null);
      
      const response = await pacientesService.listar(
        busquedaActiva ? { buscar: busquedaActiva } : undefined
      );
      
      if (response.exito) {
        setPacientes(response.pacientes);
      } else {
        setError("Error al cargar los pacientes");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Error al conectar con el servidor");
    } finally {
      setCargando(false);
    }
  };

  const handleBuscar = (e: React.FormEvent) => {
    e.preventDefault();
    setBusquedaActiva(busqueda);
  };

  const limpiarBusqueda = () => {
    setBusqueda("");
    setBusquedaActiva("");
  };

  const formatearFecha = (fecha: string | null) => {
    if (!fecha) return "Sin citas";
    return new Date(fecha).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getSexoLabel = (sexo: string) => {
    switch (sexo) {
      case 'M': return 'Masculino';
      case 'F': return 'Femenino';
      default: return 'Otro';
    }
  };

  const getColorEspecialidad = (especialidad: string) => {
    const colores: Record<string, string> = {
      'Medicina General': 'bg-[#79b236]/10 text-[#79b236] border border-[#79b236]/20',
      'Medicina Interna': 'bg-[#5fa7c1]/10 text-[#5fa7c1] border border-[#5fa7c1]/20',
      'Cardiología': 'bg-[#79b236]/10 text-[#79b236] border border-[#79b236]/20',
      'Dermatología': 'bg-[#5fa7c1]/10 text-[#5fa7c1] border border-[#5fa7c1]/20',
      'Pediatría': 'bg-[#79b236]/10 text-[#79b236] border border-[#79b236]/20',
      'Neurología': 'bg-[#5fa7c1]/10 text-[#5fa7c1] border border-[#5fa7c1]/20',
      'Oftalmología': 'bg-[#79b236]/10 text-[#79b236] border border-[#79b236]/20',
      'Traumatología': 'bg-[#5fa7c1]/10 text-[#5fa7c1] border border-[#5fa7c1]/20',
      'Ginecología': 'bg-[#79b236]/10 text-[#79b236] border border-[#79b236]/20',
    };
    return colores[especialidad] || 'bg-gray-100 text-gray-800 border border-gray-200';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground flex items-center gap-3">
            <Users className="w-7 h-7 sm:w-8 sm:h-8 text-primary" />
            Pacientes
          </h1>
          <p className="text-muted-foreground mt-1 text-sm sm:text-base">
            Lista de pacientes que han agendado citas médicas
          </p>
        </div>

        {/* Búsqueda + Estadísticas en una fila */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Búsqueda */}

          {/* Estadísticas */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-[#5fa7c1]/10 rounded-full border border-[#5fa7c1]/20">
                  <Users className="h-6 w-6 text-[#5fa7c1]" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{pacientes.length}</p>
                  <p className="text-sm text-muted-foreground">Total pacientes</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-[#79b236]/10 rounded-full border border-[#79b236]/20">
                  <Calendar className="h-6 w-6 text-[#79b236]" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {pacientes.reduce((sum, p) => sum + p.total_citas, 0)}
                  </p>
                  <p className="text-sm text-muted-foreground">Total citas</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-100 rounded-full">
                  <Stethoscope className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {[...new Set(pacientes.flatMap(p => p.especialidades))].length}
                  </p>
                  <p className="text-sm text-muted-foreground">Especialidades</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="sm:col-span-2 lg:col-span-1">
            <CardContent className="pt-6">
              <form onSubmit={handleBuscar} className="space-y-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Buscar por nombre..."
                    value={busqueda}
                    onChange={(e) => setBusqueda(e.target.value)}
                    className="pl-9 w-full"
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" variant="default" size="sm" className="flex-1">
                    Buscar
                  </Button>
                  {busquedaActiva && (
                    <Button type="button" variant="outline" size="sm" onClick={limpiarBusqueda} className="flex-1">
                      Limpiar
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Estado de carga y error */}
        {cargando && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-[#5fa7c1]" />
            <span className="ml-2 text-muted-foreground">Cargando pacientes...</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Lista de pacientes */}
        {!cargando && !error && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {pacientes.length === 0 ? (
              <Card className="col-span-full">
                <CardContent className="py-12 text-center">
                  <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-lg font-medium text-muted-foreground">
                    No se encontraron pacientes
                  </p>
                  {busquedaActiva && (
                    <p className="text-sm text-muted-foreground mt-2">
                      Intenta con otra búsqueda
                    </p>
                  )}
                </CardContent>
              </Card>
            ) : (
              pacientes.map((paciente) => (
                <Card key={paciente.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-[#5fa7c1]/10 rounded-full border border-[#5fa7c1]/20">
                          <User className="h-5 w-5 text-[#5fa7c1]" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <CardTitle className="text-base sm:text-lg truncate">{paciente.nombre_completo}</CardTitle>
                          <p className="text-xs sm:text-sm text-muted-foreground">
                            {paciente.edad} años • {getSexoLabel(paciente.sexo)}
                          </p>
                        </div>
                      </div>
                      <Badge variant={paciente.activo ? "default" : "secondary"}>
                        {paciente.activo ? "Activo" : "Inactivo"}
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {/* Información de contacto (parcialmente oculta) */}
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <span className="font-mono">{paciente.telefono_oculto}</span>
                      </div>
                      <div className="flex items-center gap-2 min-w-0">
                        <Mail className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <span className="font-mono text-sm truncate">{paciente.email_oculto}</span>
                      </div>
                    </div>

                    {/* Estadísticas de citas */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-sm bg-muted/50 rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <span>
                          <strong>{paciente.total_citas}</strong> {paciente.total_citas === 1 ? 'cita' : 'citas'}
                        </span>
                      </div>
                      <div className="text-muted-foreground text-xs sm:text-sm">
                        Última: {formatearFecha(paciente.ultima_cita)}
                      </div>
                    </div>

                    {/* Especialidades consultadas */}
                    {paciente.especialidades.length > 0 && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                          <Stethoscope className="h-3 w-3" />
                          Especialidades consultadas:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {paciente.especialidades.map((esp, index) => (
                            <Badge
                              key={index}
                              variant="outline"
                              className={getColorEspecialidad(esp)}
                            >
                              {esp}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default PacientesPage;