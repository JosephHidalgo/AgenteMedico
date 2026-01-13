'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { medicosService, Medico } from '@/lib/api';
import { Phone, Mail, Award } from 'lucide-react';

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
    'Psicología': 'bg-[#5fa7c1]/10 text-[#5fa7c1] border border-[#5fa7c1]/20',
  };
  return colores[especialidad] || 'bg-gray-100 text-gray-800 border border-gray-200';
};

export default function MedicosPage() {
  const [medicos, setMedicos] = useState<Medico[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargarMedicos = async () => {
      try {
        setCargando(true);
        const response = await medicosService.listar();
        if (response.exito) {
          setMedicos(response.medicos);
        }
      } catch (error) {
        console.error('Error al cargar médicos:', error);
      } finally {
        setCargando(false);
      }
    };

    cargarMedicos();
  }, []);

  if (cargando) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Médicos</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Directorio de médicos especialistas
            </p>
          </div>
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-6 bg-muted rounded w-3/4"></div>
                  <div className="h-4 bg-muted rounded w-1/2 mt-2"></div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="h-4 bg-muted rounded"></div>
                    <div className="h-4 bg-muted rounded"></div>
                    <div className="h-4 bg-muted rounded w-5/6"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Médicos</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Directorio de médicos especialistas
            </p>
          </div>
        </div>

        {/* Grid de Médicos */}
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {medicos.map((medico) => (
            <Card key={medico.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-1">
                      {medico.nombre} {medico.apellido_paterno}
                    </CardTitle>
                    <Badge className={getColorEspecialidad(medico.especialidad)}>
                      {medico.especialidad}
                    </Badge>
                  </div>
                  {medico.activo && (
                    <div className="w-3 h-3 bg-[#79b236] rounded-full border border-[#79b236]" title="Activo"></div>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Cédula Profesional */}
                <div className="flex items-center gap-2 text-sm">
                  <Award className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  <div>
                    <p className="text-muted-foreground text-xs">Cédula Profesional</p>
                    <p className="font-medium">{medico.cedula_profesional}</p>
                  </div>
                </div>

                {/* Teléfono */}
                <div className="flex items-center gap-2 text-sm">
                  <Phone className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  <div>
                    <p className="text-muted-foreground text-xs">Teléfono</p>
                    <p className="font-medium">{medico.telefono}</p>
                  </div>
                </div>

                {/* Email */}
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  <div className="overflow-hidden">
                    <p className="text-muted-foreground text-xs">Email</p>
                    <p className="font-medium truncate">{medico.email}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Mensaje si no hay médicos */}
        {medicos.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">No hay médicos registrados en el sistema.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
