"use client";

import { ReactNode } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
  noPadding?: boolean;
}

export default function DashboardLayout({ children, noPadding = false }: DashboardLayoutProps) {
  return (
    <div className={noPadding ? "" : "p-8"}>
      {children}
    </div>
  );
}
