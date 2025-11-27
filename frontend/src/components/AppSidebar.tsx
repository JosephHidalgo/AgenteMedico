"use client";

import { Home, Calendar, Users, GraduationCap, Bot, Heart } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const navigation = [
  { name: "Inicio", href: "/", icon: Home },
  { name: "Asistente Virtual", href: "/nueva-cita", icon: Bot },
  { name: "Pacientes", href: "/pacientes", icon: Users },
  { name: "Calendario de citas", href: "/calendario", icon: Calendar },
  { name: "Médicos", href: "/medicos", icon: GraduationCap },
  { name: "Créditos", href: "/creditos", icon: Heart }
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar className="border-r border-sidebar-border bg-sidebar">
      {/* Logo Header */}
      <SidebarHeader className="border-b border-sidebar-border px-6 py-4">
        <div className="flex items-center gap-3">
            <Image src="/logo.svg" alt="Logo" width={28} height={28} className="w-7 h-auto" />
          <div>
            <h1 className="text-lg font-bold text-sidebar-foreground">Sistema de Citas</h1>
            <p className="text-xs text-muted-foreground">Gestión Médica</p>
          </div>
        </div>
      </SidebarHeader>

      {/* Navigation */}
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <SidebarMenuItem key={item.name}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      className={cn(
                        "transition-all",
                        isActive
                          ? "bg-sidebar-accent text-sidebar-primary shadow-sm font-medium"
                          : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-primary"
                      )}
                    >
                      <Link href={item.href} className="flex items-center gap-3">
                        <item.icon className="h-5 w-5" />
                        <span>{item.name}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* Footer - System Info */}
      <SidebarFooter className="border-t border-sidebar-border p-4">
        <div className="flex items-center gap-3">
            <Image src="/logo.svg" alt="Logo" width={24} height={24} className="w-6 h-auto" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-foreground truncate">
              Sistema Público
            </p>
            <p className="text-xs text-muted-foreground truncate">
              Acceso abierto
            </p>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
