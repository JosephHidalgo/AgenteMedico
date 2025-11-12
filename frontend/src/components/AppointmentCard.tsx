import { Calendar, Clock, MapPin, User } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface AppointmentCardProps {
  doctor: string;
  specialty: string;
  date: string;
  time: string;
  location: string;
  type: "upcoming" | "today" | "past";
}

export default function AppointmentCard({
  doctor,
  specialty,
  date,
  time,
  location,
  type,
}: AppointmentCardProps) {
  const getTypeColor = () => {
    switch (type) {
      case "today":
        return "bg-secondary text-secondary-foreground";
      case "upcoming":
        return "bg-primary/10 text-primary";
      case "past":
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <Card className="p-4 transition-all hover:shadow-md">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-glow text-primary-foreground">
            <User className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">{doctor}</h3>
            <p className="text-sm text-muted-foreground">{specialty}</p>
          </div>
        </div>
        <Badge className={getTypeColor()}>
          {type === "today" ? "Hoy" : type === "upcoming" ? "Próxima" : "Pasada"}
        </Badge>
      </div>

      <div className="space-y-2 text-sm text-muted-foreground">
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

      {type !== "past" && (
        <div className="mt-4 flex gap-2">
          <Button variant="outline" size="sm" className="flex-1">
            Reprogramar
          </Button>
          <Button
            variant="default"
            size="sm"
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground"
          >
            Confirmar
          </Button>
        </div>
      )}
    </Card>
  );
}
