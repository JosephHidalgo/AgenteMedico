"use client";

import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar, Clock, MapPin, User, Stethoscope } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

const NewAppointment = () => {
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    toast.success("Cita creada exitosamente");
    setTimeout(() => router.push("/historial"), 1500);
  };

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Nueva Cita Médica
          </h1>
          <p className="text-muted-foreground">
            Completa el formulario para programar una nueva cita
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Información de la Cita</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="patient" className="flex items-center gap-2">
                    <User className="h-4 w-4 text-primary" />
                    Nombre del Paciente
                  </Label>
                  <Input
                    id="patient"
                    placeholder="Ej: Juan Pérez"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="doctor" className="flex items-center gap-2">
                    <Stethoscope className="h-4 w-4 text-primary" />
                    Doctor
                  </Label>
                  <Input
                    id="doctor"
                    placeholder="Ej: Dra. María García"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="specialty">Especialidad</Label>
                <Input
                  id="specialty"
                  placeholder="Ej: Medicina General, Cardiología, etc."
                  required
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="date" className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-primary" />
                    Fecha
                  </Label>
                  <Input
                    id="date"
                    type="date"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="time" className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-primary" />
                    Hora
                  </Label>
                  <Input
                    id="time"
                    type="time"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="location" className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-primary" />
                  Ubicación
                </Label>
                <Input
                  id="location"
                  placeholder="Ej: Consulta 203, Clínica Central"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Notas adicionales (opcional)</Label>
                <Textarea
                  id="notes"
                  placeholder="Motivo de la consulta, síntomas, etc."
                  rows={4}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => router.push("/")}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  className="flex-1"
                >
                  Crear Cita
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default NewAppointment;
