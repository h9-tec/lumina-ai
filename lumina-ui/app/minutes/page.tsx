"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import apiClient from "@/lib/api-client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { FileCheck, Download, CheckCircle2, Calendar, Users } from "lucide-react"
import ReactMarkdown from "react-markdown"

export default function MinutesPage() {
  const [selectedMinutes, setSelectedMinutes] = useState<string | null>(null)
  const [format, setFormat] = useState<"markdown" | "json">("markdown")

  const { data, isLoading } = useQuery({
    queryKey: ["minutes"],
    queryFn: () => apiClient.getAllMinutes(),
  })

  const { data: minutesContent } = useQuery({
    queryKey: ["minutes", selectedMinutes, format],
    queryFn: () => apiClient.getMinutes(selectedMinutes!, format),
    enabled: !!selectedMinutes,
  })

  const minutes = data?.minutes || []

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <p className="text-lg text-muted-foreground">Loading meeting minutes...</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Meeting Minutes</h1>
          <p className="mt-2 text-muted-foreground">
            AI-generated summaries and action items from meetings
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Minutes List */}
          <div className="lg:col-span-1">
            <div className="rounded-lg border bg-card">
              <div className="border-b p-4">
                <h2 className="font-semibold">All Minutes ({minutes.length})</h2>
              </div>
              <div className="max-h-[600px] overflow-y-auto">
                {minutes.length > 0 ? (
                  minutes.map((minute) => (
                    <button
                      key={minute.meeting_id}
                      onClick={() => setSelectedMinutes(minute.meeting_id)}
                      className={`w-full border-b p-4 text-left transition-colors last:border-0 hover:bg-muted/50 ${
                        selectedMinutes === minute.meeting_id
                          ? "bg-primary/10"
                          : ""
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <FileCheck className="mt-1 h-5 w-5 flex-shrink-0 text-success" />
                        <div className="flex-1 overflow-hidden">
                          <p className="truncate font-medium">
                            {minute.meeting_title || minute.meeting_id}
                          </p>
                          <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {new Date(minute.meeting_date || minute.created_at).toLocaleDateString()}
                            </span>
                            {minute.attendees && (
                              <span className="flex items-center gap-1">
                                <Users className="h-3 w-3" />
                                {minute.attendees.length}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="p-8 text-center">
                    <p className="text-sm text-muted-foreground">
                      No meeting minutes found
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Minutes Viewer */}
          <div className="lg:col-span-2">
            {selectedMinutes && minutesContent ? (
              <div className="rounded-lg border bg-card">
                <div className="flex items-center justify-between border-b p-4">
                  <div>
                    <h2 className="font-semibold">
                      {minutesContent.meeting_title || selectedMinutes}
                    </h2>
                    <p className="text-sm text-muted-foreground">
                      {new Date(minutesContent.meeting_date || minutesContent.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <select
                      value={format}
                      onChange={(e) => setFormat(e.target.value as "markdown" | "json")}
                      className="rounded-lg border bg-background px-3 py-1 text-sm"
                    >
                      <option value="markdown">Markdown</option>
                      <option value="json">JSON</option>
                    </select>
                    <button className="rounded-lg p-2 text-accent hover:bg-accent/10">
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <div className="max-h-[600px] overflow-y-auto p-6">
                  {format === "markdown" ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown>{minutesContent.content || ""}</ReactMarkdown>
                    </div>
                  ) : (
                    <pre className="overflow-x-auto rounded-lg bg-muted p-4 text-xs">
                      {JSON.stringify(minutesContent, null, 2)}
                    </pre>
                  )}

                  {/* Action Items */}
                  {minutesContent.action_items && minutesContent.action_items.length > 0 && (
                    <div className="mt-6 rounded-lg border bg-muted/30 p-4">
                      <h3 className="mb-3 flex items-center gap-2 font-semibold">
                        <CheckCircle2 className="h-5 w-5 text-success" />
                        Action Items
                      </h3>
                      <ul className="space-y-2">
                        {minutesContent.action_items.map((item: any, idx: number) => (
                          <li key={idx} className="flex items-start gap-2 text-sm">
                            <span className="mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-primary" />
                            <span>
                              {typeof item === "string" ? item : item.description || item.task}
                              {item.assignee && (
                                <span className="ml-2 text-xs text-muted-foreground">
                                  (@{item.assignee})
                                </span>
                              )}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex h-full min-h-[400px] items-center justify-center rounded-lg border bg-card">
                <div className="text-center">
                  <FileCheck className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-4 font-semibold">No minutes selected</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Select meeting minutes from the list to view
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
