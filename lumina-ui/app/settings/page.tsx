"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import apiClient from "@/lib/api-client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Settings as SettingsIcon, Save, Calendar, Cpu, Mail, Mic } from "lucide-react"
import { toast } from "sonner"

type Tab = "calendar" | "ai" | "email" | "recording"

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("calendar")
  const queryClient = useQueryClient()

  const { data: config, isLoading } = useQuery({
    queryKey: ["config"],
    queryFn: () => apiClient.getConfig(),
  })

  const updateMutation = useMutation({
    mutationFn: (newConfig: any) => apiClient.updateConfig(newConfig),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["config"] })
      toast.success("Settings saved successfully")
    },
    onError: () => {
      toast.error("Failed to save settings")
    },
  })

  const tabs = [
    { id: "calendar" as Tab, name: "Calendar", icon: Calendar },
    { id: "ai" as Tab, name: "AI Models", icon: Cpu },
    { id: "email" as Tab, name: "Email", icon: Mail },
    { id: "recording" as Tab, name: "Recording", icon: Mic },
  ]

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <p className="text-lg text-muted-foreground">Loading settings...</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="mt-2 text-muted-foreground">
            Configure Lumina AI to match your preferences
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-4">
          {/* Tabs Sidebar */}
          <div className="lg:col-span-1">
            <div className="rounded-lg border bg-card p-2">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                        activeTab === tab.id
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-muted"
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      {tab.name}
                    </button>
                  )
                })}
              </nav>
            </div>
          </div>

          {/* Settings Content */}
          <div className="lg:col-span-3">
            <div className="rounded-lg border bg-card p-6">
              {activeTab === "calendar" && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold">Calendar Settings</h2>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Configure automatic meeting detection and joining
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          defaultChecked={config?.calendar?.auto_join}
                          className="h-4 w-4 rounded"
                        />
                        <span className="text-sm font-medium">
                          Automatically join meetings from calendar
                        </span>
                      </label>
                      <p className="ml-6 mt-1 text-xs text-muted-foreground">
                        Lumina will join meetings 1-2 minutes before start time
                      </p>
                    </div>

                    <div>
                      <label className="text-sm font-medium">
                        Join before start (minutes)
                      </label>
                      <input
                        type="number"
                        defaultValue={config?.calendar?.join_before_minutes || 2}
                        min={1}
                        max={10}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium">Calendar Check Interval (seconds)</label>
                      <input
                        type="number"
                        defaultValue={config?.calendar?.check_interval || 60}
                        min={30}
                        max={300}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "ai" && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold">AI Model Settings</h2>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Select AI providers and models for processing
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">LLM Provider</label>
                      <select
                        defaultValue={config?.llm?.provider || "ollama"}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      >
                        {config?.llm?.available_providers?.map((provider: string) => (
                          <option key={provider} value={provider}>
                            {provider}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">LLM Model</label>
                      <input
                        type="text"
                        defaultValue={config?.llm?.model || "llama3"}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      />
                      <p className="mt-1 text-xs text-muted-foreground">
                        Used for generating meeting minutes and summaries
                      </p>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Whisper Model</label>
                      <select
                        defaultValue={config?.whisper?.model || "base"}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      >
                        {config?.whisper?.available_models?.map((model: string) => (
                          <option key={model} value={model}>
                            {model}
                          </option>
                        ))}
                      </select>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Larger models are more accurate but slower
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "email" && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold">Email Settings</h2>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Configure email delivery for meeting minutes
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">SMTP Server</label>
                      <input
                        type="text"
                        placeholder="smtp.gmail.com"
                        defaultValue={config?.email?.smtp_server}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">SMTP Port</label>
                        <input
                          type="number"
                          defaultValue={config?.email?.smtp_port || 587}
                          className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                        />
                      </div>

                      <div>
                        <label className="flex items-center gap-2 pt-8">
                          <input
                            type="checkbox"
                            defaultChecked={config?.email?.use_tls}
                            className="h-4 w-4 rounded"
                          />
                          <span className="text-sm font-medium">Use TLS</span>
                        </label>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium">From Email</label>
                      <input
                        type="email"
                        placeholder="lumina@example.com"
                        defaultValue={config?.email?.from_email}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      />
                    </div>

                    <div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          defaultChecked={config?.email?.auto_send_minutes}
                          className="h-4 w-4 rounded"
                        />
                        <span className="text-sm font-medium">
                          Automatically send minutes after meetings
                        </span>
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "recording" && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold">Recording Settings</h2>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Configure audio recording and transcription
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          defaultChecked={config?.recording?.auto_record}
                          className="h-4 w-4 rounded"
                        />
                        <span className="text-sm font-medium">
                          Automatically record all meetings
                        </span>
                      </label>
                    </div>

                    <div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          defaultChecked={config?.recording?.auto_transcribe}
                          className="h-4 w-4 rounded"
                        />
                        <span className="text-sm font-medium">
                          Automatically transcribe recordings
                        </span>
                      </label>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Audio Format</label>
                      <select
                        defaultValue={config?.recording?.format || "wav"}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      >
                        <option value="wav">WAV</option>
                        <option value="mp3">MP3</option>
                        <option value="m4a">M4A</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Sample Rate (Hz)</label>
                      <select
                        defaultValue={config?.recording?.sample_rate || 16000}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      >
                        <option value={8000}>8000 Hz (Low)</option>
                        <option value={16000}>16000 Hz (Standard)</option>
                        <option value={44100}>44100 Hz (High)</option>
                        <option value={48000}>48000 Hz (Studio)</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Storage Location</label>
                      <input
                        type="text"
                        defaultValue={config?.recording?.storage_path || "./recordings"}
                        className="mt-2 w-full rounded-lg border bg-background px-4 py-2"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Save Button */}
              <div className="mt-8 flex justify-end">
                <button
                  onClick={() => updateMutation.mutate(config)}
                  disabled={updateMutation.isPending}
                  className="flex items-center gap-2 rounded-lg bg-primary px-6 py-2 font-medium text-primary-foreground hover:opacity-90 disabled:opacity-50"
                >
                  <Save className="h-4 w-4" />
                  {updateMutation.isPending ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
