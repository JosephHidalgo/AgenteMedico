"use client";

import { useRouter } from "next/navigation";
import { MessageCircle } from "lucide-react";

export default function VirtualAssistant() {
  const router = useRouter();

  const handleClick = () => {
    router.push('/nueva-cita');
  };

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-8 right-8 z-50 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-primary to-secondary text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 group"
      aria-label="Abrir asistente virtual"
    >
      <MessageCircle className="h-8 w-8 group-hover:animate-pulse" />
      <span className="absolute -top-1 -right-1 flex h-5 w-5">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75"></span>
        <span className="relative inline-flex rounded-full h-5 w-5 bg-secondary"></span>
      </span>
    </button>
  );
}
