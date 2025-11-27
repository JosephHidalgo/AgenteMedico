import { Calendar, Clock, MapPin, User, Stethoscope } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface AppointmentCardProps {
  doctor: string;
  specialty: string;
  patient?: string;
  date: string;
  time: string;
  location: string;
  status?: "AGENDADA" | "COMPLETADA" | "CANCELADA" | "EXPIRADA";
  isToday?: boolean;
}

export default function AppointmentCard({
  doctor,
  specialty,
  patient,
  date,
  time,
  location,
  status = "AGENDADA",
  isToday = false,
}: AppointmentCardProps) {
  const getStatusColor = () => {
    switch (status) {
      case "AGENDADA":
        return "bg-green-500/10 text-green-700 dark:text-green-400";
      case "COMPLETADA":
        return "bg-blue-500/10 text-blue-700 dark:text-blue-400";
      case "CANCELADA":
        return "bg-red-500/10 text-red-700 dark:text-red-400";
      case "EXPIRADA":
        return "bg-gray-500/10 text-gray-700 dark:text-gray-400";
      default:
        return "bg-gray-500/10 text-gray-700 dark:text-gray-400";
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case "AGENDADA":
        return "Agendada";
      case "COMPLETADA":
        return "Completada";
      case "CANCELADA":
        return "Cancelada";
      case "EXPIRADA":
        return "Expirada";
      default:
        return status;
    }
  };

  return (
    <Card className={`p-4 transition-all hover:shadow-md ${isToday ? 'border-2 border-secondary shadow-lg' : ''}`}>
      {/* Paciente como protagonista */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br ${isToday ? 'from-secondary to-secondary/80' : 'from-primary to-primary-glow'} text-primary-foreground`}>
            <User className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Paciente</p>
            <h3 className="font-semibold text-foreground">{patient || "Sin asignar"}</h3>
          </div>
        </div>
        <div className="flex flex-col gap-1 items-end">
          {isToday && (
            <Badge className="bg-secondary text-secondary-foreground">
              Hoy
            </Badge>
          )}
          <Badge className={getStatusColor()}>
            {getStatusLabel()}
          </Badge>
        </div>
      </div>

      <div className="space-y-2 text-sm text-muted-foreground">
        {/* Médico */}
        <div className="flex items-center gap-2">
          <Stethoscope className="h-4 w-4" />
          <span className="font-medium text-foreground">{doctor}</span>
          <span>· {specialty}</span>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          <span>{date}</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          <span>{time}</span>
        </div>
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4" />
          <span>{location}</span>
        </div>
      </div>
    </Card>
  );
}
