"use client";

import Image from "next/image";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
    User,
    Globe,
    Code2,
    Calendar,
    Heart,
    ExternalLink,
    Activity
} from "lucide-react";

const CreditosPage = () => {
    const desarrollador = {
        nombre: "Joseph Hidalgo",
        rol: "Full Stack Developer",
        github: "https://github.com/JosephHidalgo",
        linkedin: "https://www.linkedin.com/in/henry-hidalgo-neira-5ba034299/",
        email: "hidalgoneirahenry@gmail.com",
        portfolio: "https://josephhidalgo.dev",
        año: "2025"
    };

    const techStack = [
        { nombre: "Next.js", imagen: "/nextjs.svg", descripcion: "Framework React" },
        { nombre: "TypeScript", imagen: "/typescript.svg", descripcion: "Tipado estático" },
        { nombre: "Tailwind CSS", imagen: "/tailwindcss.svg", descripcion: "Estilos utilitarios" },
        { nombre: "Django", imagen: "/django.svg", descripcion: "Backend Python" },
        { nombre: "PostgreSQL", imagen: "/postgresql.svg", descripcion: "Base de datos" },
        { nombre: "Redis", imagen: "/redis.svg", descripcion: "Caché y sesiones" },
    ];

    return (
        <DashboardLayout>
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <div className="text-center space-y-4">
                    <h1 className="text-4xl font-bold text-foreground">
                        Créditos del Proyecto
                    </h1>
                </div>

                {/* Desarrollador Card */}
                <Card className="overflow-hidden border-border">
                    <div className="bg-gradient-to-r from-primary/80 to-secondary/80 h-24" />
                    <CardContent className="relative pt-0">
                        <div className="flex flex-col sm:flex-row items-center sm:items-end gap-4 -mt-12">
                            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-card border-4 border-card shadow-lg">
                                <User className="h-12 w-12 text-primary" />
                            </div>
                            <div className="text-center sm:text-left pb-2">
                                <h2 className="text-2xl font-bold text-foreground">{desarrollador.nombre}</h2>
                                <p className="text-muted-foreground">{desarrollador.rol}</p>
                            </div>
                            <div className="sm:ml-auto flex items-center gap-2">
                                <Badge variant="secondary" className="gap-1">
                                    <Calendar className="h-3 w-3" />
                                    {desarrollador.año}
                                </Badge>
                            </div>
                        </div>

                        <Separator className="my-6" />

                        {/* Links de contacto */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <a
                                href={desarrollador.github}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-3 p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors group"
                            >
                                <Image src="/github.svg" alt="GitHub" width={30} height={30} className="w-[30px] h-auto" />

                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-foreground">GitHub</p>
                                    <p className="text-sm text-muted-foreground truncate">@JosephHidalgo</p>
                                </div>
                                <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                            </a>

                            <a
                                href={desarrollador.linkedin}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-3 p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors group"
                            >
                                <Image src="/linkedin.svg" alt="LinkedIn" width={40} height={40} className="w-[40px] h-auto" />
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-foreground">LinkedIn</p>
                                    <p className="text-sm text-muted-foreground truncate">Perfil profesional</p>
                                </div>
                                <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                            </a>

                            <a
                                href={`mailto:${desarrollador.email}`}
                                className="flex items-center gap-3 p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors group"
                            >
                                <Image src="/gmail.svg" alt="Gmail" width={30} height={30} className="w-[30px] h-auto" />

                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-foreground">Email</p>
                                    <p className="text-sm text-muted-foreground truncate">{desarrollador.email}</p>
                                </div>
                                <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                            </a>

                            <a
                                href={desarrollador.portfolio}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-3 p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors group"
                            >
                                <div className="p-2 bg-secondary rounded-lg">
                                    <Globe className="h-5 w-5 text-secondary-foreground" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-foreground">Portfolio</p>
                                    <p className="text-sm text-muted-foreground truncate">Sitio web personal</p>
                                </div>
                                <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                            </a>
                        </div>
                    </CardContent>
                </Card>

                {/* Stack Tecnológico con SVGs */}
                <Card className="border-border">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-foreground">
                            <Code2 className="h-5 w-5 text-primary" />
                            Stack Tecnológico para este Proyecto
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-6">
                            {techStack.map((tech) => (
                                <div
                                    key={tech.nombre}
                                    className="flex flex-col items-center gap-3 p-4 rounded-lg border border-border hover:bg-accent/30 hover:border-primary/30 transition-all group"
                                >
                                    <div className="relative h-12 w-12 flex items-center justify-center">
                                        <Image
                                            src={tech.imagen}
                                            alt={tech.nombre}
                                            width={48}
                                            height={48}
                                            className="w-12 h-auto object-contain group-hover:scale-110 transition-transform"
                                        />
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm font-medium text-foreground">{tech.nombre}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Sobre el Proyecto */}
                <Card className="border-border">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-foreground">
                            <Heart className="h-5 w-5 text-destructive" />
                            Sobre el Proyecto
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4 text-muted-foreground">
                        <p>
                            Este sistema de gestión de citas médicas fue desarrollado como proyecto de portafolio
                            para demostrar competencias en desarrollo de software full stack.
                        </p>
                        <p className="pt-2">
                            <strong className="text-foreground">Nota:</strong> Este es un proyecto de demostración
                            y no está destinado para uso en producción con datos médicos reales.
                        </p>
                    </CardContent>
                </Card>

                {/* Footer con enlace al repo */}
                <div className="text-center pb-8">
                    <a
                        href="https://github.com/JosephHidalgo/AgenteMedico"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        <Button variant="outline" size="lg" className="gap-2">
                            <Image src="/github.svg" alt="GitHub" width={20} height={20} className="w-5 h-auto" />
                            Ver código en GitHub
                            <ExternalLink className="h-4 w-4" />
                        </Button>
                    </a>
                    <p className="mt-4 text-sm text-muted-foreground">
                        Hecho con <Heart className="inline h-4 w-4 text-destructive" /> por {desarrollador.nombre} • {desarrollador.año}
                    </p>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default CreditosPage;
