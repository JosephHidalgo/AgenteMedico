import DashboardLayout from "@/components/DashboardLayout";
import VirtualAssistant from "@/components/VirtualAssistant";
import HealthCard from "@/components/HealthCard";
import AppointmentCard from "@/components/AppointmentCard";
import { Activity, Calendar, Heart, Pill, TrendingUp, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Index = () => {
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
            value="5"
            subtitle="Citas programadas para hoy"
            iconClassName="bg-secondary/10 text-secondary"
          />
          <HealthCard
            title="Citas Esta Semana"
            icon={Activity}
            value="18"
            subtitle="Próximas 7 días"
            iconClassName="bg-primary/10 text-primary"
          />
          <HealthCard
            title="Total de Pacientes"
            icon={Heart}
            value="247"
            subtitle="Pacientes registrados"
            iconClassName="bg-accent/10 text-accent"
          />
          <HealthCard
            title="Doctores Activos"
            icon={Pill}
            value="12"
            subtitle="Disponibles hoy"
            iconClassName="bg-destructive/10 text-destructive"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Today's Appointments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-primary" />
                Citas de Hoy
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <AppointmentCard
                doctor="Dra. María García"
                specialty="Medicina General"
                date="1 Nov 2025"
                time="10:00 AM"
                location="Consulta 203, Clínica Central"
                type="today"
              />
              <AppointmentCard
                doctor="Dr. Carlos Rodríguez"
                specialty="Cardiología"
                date="1 Nov 2025"
                time="3:30 PM"
                location="Consulta 105, Hospital Norte"
                type="today"
              />
            </CardContent>
          </Card>

          {/* Upcoming Appointments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-secondary" />
                Próximas Citas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <AppointmentCard
                doctor="Dr. Luis Martínez"
                specialty="Pediatría"
                date="2 Nov 2025"
                time="9:00 AM"
                location="Consulta 301, Clínica Infantil"
                type="upcoming"
              />
              <AppointmentCard
                doctor="Dra. Ana López"
                specialty="Dermatología"
                date="3 Nov 2025"
                time="11:30 AM"
                location="Consulta 405, Centro Médico"
                type="upcoming"
              />
            </CardContent>
          </Card>
        </div>

        {/* System Alerts */}
        <Card className="border-l-4 border-l-secondary">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-secondary" />
              Notificaciones del Sistema
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="flex h-2 w-2 mt-2 rounded-full bg-secondary" />
                <div>
                  <p className="font-medium text-foreground">
                    Confirmación pendiente
                  </p>
                  <p className="text-sm text-muted-foreground">2 citas requieren confirmación</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex h-2 w-2 mt-2 rounded-full bg-primary" />
                <div>
                  <p className="font-medium text-foreground">
                    Nuevas citas registradas
                  </p>
                  <p className="text-sm text-muted-foreground">
                    3 citas nuevas en las últimas 24 horas
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Virtual Assistant */}
      <VirtualAssistant />
    </DashboardLayout>
  );
};

export default Index;
