"use client"

import { useTheme } from "next-themes"
import { Moon, Sun, Bell, User } from "lucide-react"
import { useEffect, useState } from "react"

export function Header() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <header className="flex h-16 items-center justify-between border-b bg-card px-6">
        <div className="flex-1" />
        <div className="flex items-center gap-4">
          <div className="h-9 w-9" />
          <div className="h-9 w-9" />
          <div className="h-9 w-9" />
        </div>
      </header>
    )
  }

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-6">
      {/* Breadcrumb / Page Title - will be dynamic later */}
      <div className="flex-1">
        <h2 className="text-lg font-semibold text-foreground">Dashboard</h2>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <button
          className="relative flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-destructive" />
        </button>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </button>

        {/* User Menu */}
        <button
          className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-opacity hover:opacity-90"
          aria-label="User menu"
        >
          <User className="h-5 w-5" />
        </button>
      </div>
    </header>
  )
}
