"use client"

import { useQuery } from "@tanstack/react-query"
import apiClient from "@/lib/api-client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

export default function DashboardPage() {
  const { data: status, isLoading } = useQuery({
    queryKey: ["status"],
    queryFn: () => apiClient.getStatus(),
  })

  const { data: meetings } = useQuery({
    queryKey: ["meetings"],
    queryFn: () => apiClient.getUpcomingMeetings(),
  })

  const { data: recordings } = useQuery({
    queryKey: ["recordings"],
    queryFn: () => apiClient.getRecordings(),
  })

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <p className="text-lg text-muted-foreground">Loading...</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Welcome back</h1>
          <p className="mt-2 text-muted-foreground">
            Here's what's happening with your meetings today
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <div className="rounded-lg border bg-card p-6">
            <h3 className="text-sm font-medium text-muted-foreground">System Status</h3>
            <p className="mt-2 text-3xl font-bold">{status?.status || "Unknown"}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Version {status?.version || "N/A"}
            </p>
          </div>

          <div className="rounded-lg border bg-card p-6">
            <h3 className="text-sm font-medium text-muted-foreground">Active Meetings</h3>
            <p className="mt-2 text-3xl font-bold">{status?.active_meetings || 0}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Calendar: {status?.calendar_monitor_active ? "Active" : "Inactive"}
            </p>
          </div>

          <div className="rounded-lg border bg-card p-6">
            <h3 className="text-sm font-medium text-muted-foreground">Total Recordings</h3>
            <p className="mt-2 text-3xl font-bold">{recordings?.total || 0}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              {recordings?.recordings.length || 0} available
            </p>
          </div>
        </div>

        {/* Upcoming Meetings */}
        <div className="rounded-lg border bg-card p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Upcoming Meetings</h2>
          {meetings && meetings.meetings.length > 0 ? (
            <div className="space-y-3">
              {meetings.meetings.map((meeting) => (
                <div key={meeting.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                  <div>
                    <p className="font-medium">{meeting.title || meeting.summary}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(meeting.start).toLocaleString()}
                    </p>
                  </div>
                  <a
                    href={meeting.meetLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline"
                  >
                    Join
                  </a>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No upcoming meetings</p>
          )}
        </div>

        {/* Recent Recordings */}
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-xl font-bold mb-4">Recent Recordings</h2>
          {recordings && recordings.recordings.length > 0 ? (
            <div className="space-y-3">
              {recordings.recordings.slice(0, 5).map((recording) => (
                <div key={recording.meeting_id} className="flex items-center justify-between border-b pb-3 last:border-0">
                  <div>
                    <p className="font-medium">{recording.meeting_id}</p>
                    <p className="text-sm text-muted-foreground">
                      {recording.size_mb.toFixed(2)} MB
                    </p>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {new Date(recording.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No recordings available</p>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
