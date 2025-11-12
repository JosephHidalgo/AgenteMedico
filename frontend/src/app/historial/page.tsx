import DashboardLayout from "@/components/DashboardLayout";
import AppointmentCard from "@/components/AppointmentCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileText } from "lucide-react";

const AppointmentHistory = () => {
  const todayAppointments = [
    {
      doctor: "Dra. María García",
      specialty: "Medicina General",
      date: "1 Nov 2025",
      time: "10:00 AM",
      location: "Consulta 203, Clínica Central",
      type: "today" as const,
    },
    {
      doctor: "Dr. Carlos Rodríguez",
      specialty: "Cardiología",
      date: "1 Nov 2025",
      time: "3:30 PM",
      location: "Consulta 105, Hospital Norte",
      type: "today" as const,
    },
  ];

  const upcomingAppointments = [
    {
      doctor: "Dr. Luis Martínez",
      specialty: "Pediatría",
      date: "2 Nov 2025",
      time: "9:00 AM",
      location: "Consulta 301, Clínica Infantil",
      type: "upcoming" as const,
    },
    {
      doctor: "Dra. Ana López",
      specialty: "Dermatología",
      date: "3 Nov 2025",
      time: "11:30 AM",
      location: "Consulta 405, Centro Médico",
      type: "upcoming" as const,
    },
    {
      doctor: "Dr. Roberto Sánchez",
      specialty: "Oftalmología",
      date: "5 Nov 2025",
      time: "2:00 PM",
      location: "Consulta 102, Clínica Vista",
      type: "upcoming" as const,
    },
  ];

  const pastAppointments = [
    {
      doctor: "Dra. Patricia Ruiz",
      specialty: "Medicina General",
      date: "28 Oct 2025",
      time: "11:00 AM",
      location: "Consulta 203, Clínica Central",
      type: "past" as const,
    },
    {
      doctor: "Dr. Fernando Torres",
      specialty: "Traumatología",
      date: "25 Oct 2025",
      time: "4:00 PM",
      location: "Consulta 501, Hospital General",
      type: "past" as const,
    },
    {
      doctor: "Dra. Isabel Morales",
      specialty: "Nutrición",
      date: "20 Oct 2025",
      time: "10:30 AM",
      location: "Consulta 302, Centro Nutricional",
      type: "past" as const,
    },
    {
      doctor: "Dr. Miguel Herrera",
      specialty: "Psicología",
      date: "15 Oct 2025",
      time: "5:00 PM",
      location: "Consulta 201, Clínica Mental",
      type: "past" as const,
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Historial de Citas
          </h1>
          <p className="text-muted-foreground">
            Visualiza todas las citas: pasadas, actuales y futuras
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Todas las Citas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="today" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="today">Hoy ({todayAppointments.length})</TabsTrigger>
                <TabsTrigger value="upcoming">Próximas ({upcomingAppointments.length})</TabsTrigger>
                <TabsTrigger value="past">Pasadas ({pastAppointments.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="today" className="space-y-4 mt-6">
                {todayAppointments.map((appointment, index) => (
                  <AppointmentCard key={index} {...appointment} />
                ))}
              </TabsContent>

              <TabsContent value="upcoming" className="space-y-4 mt-6">
                {upcomingAppointments.map((appointment, index) => (
                  <AppointmentCard key={index} {...appointment} />
                ))}
              </TabsContent>

              <TabsContent value="past" className="space-y-4 mt-6">
                {pastAppointments.map((appointment, index) => (
                  <AppointmentCard key={index} {...appointment} />
                ))}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default AppointmentHistory;
