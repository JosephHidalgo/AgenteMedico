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
      'Medicina General': 'bg-blue-100 text-blue-800',
      'Medicina Interna': 'bg-sky-100 text-sky-800',
      'Cardiología': 'bg-red-100 text-red-800',
      'Dermatología': 'bg-purple-100 text-purple-800',
      'Pediatría': 'bg-green-100 text-green-800',
      'Neurología': 'bg-yellow-100 text-yellow-800',
      'Oftalmología': 'bg-cyan-100 text-cyan-800',
      'Traumatología': 'bg-orange-100 text-orange-800',
      'Ginecología': 'bg-pink-100 text-pink-800',
    };
    return colores[especialidad] || 'bg-gray-100 text-gray-800';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
              <Users className="w-8 h-8 text-blue-600" />
              Pacientes
            </h1>
            <p className="text-muted-foreground mt-1">
              Lista de pacientes que han agendado citas médicas
            </p>
          </div>
          
          {/* Búsqueda */}
          <form onSubmit={handleBuscar} className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Buscar por nombre..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="pl-9 w-64"
              />
            </div>
            <Button type="submit" variant="default">
              Buscar
            </Button>
            {busquedaActiva && (
              <Button type="button" variant="outline" onClick={limpiarBusqueda}>
                Limpiar
              </Button>
            )}
          </form>
        </div>

        {/* Estadísticas rápidas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-100 rounded-full">
                  <Users className="h-6 w-6 text-blue-600" />
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
                <div className="p-3 bg-green-100 rounded-full">
                  <Calendar className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {pacientes.reduce((sum, p) => sum + p.total_citas, 0)}
                  </p>
                  <p className="text-sm text-muted-foreground">Total citas agendadas</p>
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
                  <p className="text-sm text-muted-foreground">Especialidades consultadas</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Estado de carga y error */}
        {cargando && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
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
                        <div className="p-2 bg-blue-100 rounded-full">
                          <User className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{paciente.nombre_completo}</CardTitle>
                          <p className="text-sm text-muted-foreground">
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
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4 text-muted-foreground" />
                        <span className="font-mono">{paciente.telefono_oculto}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4 text-muted-foreground" />
                        <span className="font-mono text-sm">{paciente.email_oculto}</span>
                      </div>
                    </div>

                    {/* Estadísticas de citas */}
                    <div className="flex items-center justify-between text-sm bg-muted/50 rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span>
                          <strong>{paciente.total_citas}</strong> {paciente.total_citas === 1 ? 'cita' : 'citas'}
                        </span>
                      </div>
                      <div className="text-muted-foreground">
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

        {/* Nota de privacidad */}
        <div className="text-center text-xs text-muted-foreground bg-muted/30 rounded-lg p-3">
          🔒 Los datos de contacto se muestran parcialmente ocultos por motivos de privacidad
        </div>
      </div>
    </DashboardLayout>
  );
};

export default PacientesPage;