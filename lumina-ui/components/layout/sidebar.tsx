"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Calendar,
  Mic,
  FileText,
  FileCheck,
  Settings,
  BarChart3,
  Sparkles,
} from "lucide-react"

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Meetings",
    href: "/meetings",
    icon: Calendar,
  },
  {
    name: "Recordings",
    href: "/recordings",
    icon: Mic,
  },
  {
    name: "Transcripts",
    href: "/transcripts",
    icon: FileText,
  },
  {
    name: "Minutes",
    href: "/minutes",
    icon: FileCheck,
  },
  {
    name: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b px-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
          <Sparkles className="h-6 w-6 text-primary-foreground" />
        </div>
        <div className="flex flex-col">
          <h1 className="text-lg font-bold">Lumina AI</h1>
          <p className="text-xs text-muted-foreground">Meeting Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <div className="rounded-lg bg-muted p-3">
          <p className="text-xs font-medium text-foreground">Need Help?</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Check the documentation or contact support
          </p>
          <Link
            href="/docs"
            className="mt-2 inline-block text-xs font-medium text-primary hover:underline"
          >
            View Docs →
          </Link>
        </div>
      </div>
    </div>
  )
}
