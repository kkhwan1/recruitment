"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Newspaper,
  FileText
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "대시보드", href: "/", icon: LayoutDashboard },
  { name: "채용 정보", href: "/jobs", icon: Briefcase },
  { name: "관련 뉴스", href: "/news", icon: Newspaper },
  { name: "분석 리포트", href: "/reports", icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col border-r border-border bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-border px-6">
        <h1 className="text-xl font-bold text-foreground">채용 분석 시스템</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-border p-4">
        <p className="text-xs text-muted-foreground">
          v0.1.0
        </p>
      </div>
    </div>
  );
}
