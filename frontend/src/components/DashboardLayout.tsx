"use client";

import { ReactNode } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
  noPadding?: boolean;
}

export default function DashboardLayout({ children, noPadding = false }: DashboardLayoutProps) {
  return (
    <div className={`${noPadding ? "" : "px-4 py-6 sm:px-6 sm:py-8"} overflow-x-hidden w-full max-w-full box-border`}>
      {children}
    </div>
  );
}
