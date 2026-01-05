import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import Image from "next/image";
import { Search, Bell, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MedBot",
  description: "Sistema de Citas Médicas",
  icons: {
    icon: "/logo.svg",
    shortcut: "/logo.svg",
    apple: "/logo.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <SidebarProvider>
          <AppSidebar />
          <main className="flex-1 w-full flex flex-col min-h-screen">
            <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border shadow-sm">
              <div className="flex h-16 items-center px-6 gap-4">
                <SidebarTrigger className="-ml-1" />
                
                <div className="flex-1" />
                
                {/* Logo y Título */}
                <div className="flex items-center gap-3">
                  <Image 
                    src="/logo.svg" 
                    alt="MedBot Logo" 
                    width={32} 
                    height={32} 
                    className="w-8 h-auto"
                  />
                  <div>
                    <h1 className="text-xl font-bold text-primary">MedBot</h1>
                  </div>
                </div>
                
                <div className="flex-1" />
              </div>
            </header>
            <div className="flex-1 flex flex-col overflow-hidden">
              {children}
            </div>
          </main>
        </SidebarProvider>
      </body>
    </html>
  );
}
