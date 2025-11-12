import { ReactNode } from "react";
import { LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface HealthCardProps {
  title: string;
  icon: LucideIcon;
  value?: string | number;
  subtitle?: string;
  children?: ReactNode;
  className?: string;
  iconClassName?: string;
}

export default function HealthCard({
  title,
  icon: Icon,
  value,
  subtitle,
  children,
  className,
  iconClassName,
}: HealthCardProps) {
  return (
    <Card className={cn("transition-all hover:shadow-lg", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className={cn("rounded-lg p-2", iconClassName)}>
          <Icon className="h-5 w-5" />
        </div>
      </CardHeader>
      <CardContent>
        {value !== undefined && (
          <div className="text-2xl font-bold text-foreground">{value}</div>
        )}
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
        {children && <div className="mt-3">{children}</div>}
      </CardContent>
    </Card>
  );
}
