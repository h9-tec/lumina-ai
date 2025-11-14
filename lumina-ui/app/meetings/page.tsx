"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import apiClient from "@/lib/api-client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Calendar, Plus, Play, StopCircle, Video, ExternalLink } from "lucide-react"
import { toast } from "sonner"
import { isValidMeetUrl } from "@/lib/utils"

export default function MeetingsPage() {
  const [showJoinDialog, setShowJoinDialog] = useState(false)
  const [meetLink, setMeetLink] = useState("")
  const [autoRecord, setAutoRecord] = useState(true)
  const queryClient = useQueryClient()

  const { data: meetings, isLoading } = useQuery({
    queryKey: ["meetings"],
    queryFn: () => apiClient.getUpcomingMeetings(),
  })

  const { data: status } = useQuery({
    queryKey: ["status"],
    queryFn: () => apiClient.getStatus(),
  })

  const joinMutation = useMutation({
    mutationFn: (data: { meetLink: string; autoRecord: boolean }) =>
      apiClient.joinMeeting(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["status"] })
      toast.success("Joining meeting...")
      setShowJoinDialog(false)
      setMeetLink("")
    },
    onError: () => {
      toast.error("Failed to join meeting")
    },
  })

  const startMonitorMutation = useMutation({
    mutationFn: () => apiClient.startCalendarMonitor(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["status"] })
      toast.success("Calendar monitoring started")
    },
  })

  const stopMonitorMutation = useMutation({
    mutationFn: () => apiClient.stopCalendarMonitor(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["status"] })
      toast.success("Calendar monitoring stopped")
    },
  })

  const handleJoin = () => {
    if (!isValidMeetUrl(meetLink)) {
      toast.error("Invalid Google Meet URL")
      return
    }
    joinMutation.mutate({ meetLink, autoRecord })
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <p className="text-lg text-muted-foreground">Loading meetings...</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Meetings</h1>
            <p className="mt-2 text-muted-foreground">
              View upcoming meetings and join manually
            </p>
          </div>
          <button
            onClick={() => setShowJoinDialog(true)}
            className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground hover:opacity-90"
          >
            <Plus className="h-5 w-5" />
            Join Meeting
          </button>
        </div>

        {/* Calendar Monitor Status */}
        <div className="mb-6 rounded-lg border bg-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold">Calendar Monitoring</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Automatically join meetings from your Google Calendar
              </p>
            </div>
            {status?.calendar_monitor_active ? (
              <button
                onClick={() => stopMonitorMutation.mutate()}
                className="flex items-center gap-2 rounded-lg bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground hover:opacity-90"
                disabled={stopMonitorMutation.isPending}
              >
                <StopCircle className="h-4 w-4" />
                Stop Monitoring
              </button>
            ) : (
              <button
                onClick={() => startMonitorMutation.mutate()}
                className="flex items-center gap-2 rounded-lg bg-success px-4 py-2 text-sm font-medium text-success-foreground hover:opacity-90"
                disabled={startMonitorMutation.isPending}
              >
                <Play className="h-4 w-4" />
                Start Monitoring
              </button>
            )}
          </div>
        </div>

        {/* Upcoming Meetings */}
        <div className="rounded-lg border bg-card">
          <div className="border-b p-4">
            <h2 className="font-semibold">Upcoming Meetings</h2>
          </div>
          <div className="divide-y">
            {meetings && meetings.meetings.length > 0 ? (
              meetings.meetings.map((meeting) => (
                <div
                  key={meeting.id}
                  className="flex items-center justify-between p-6 hover:bg-muted/30"
                >
                  <div className="flex items-start gap-4">
                    <div className="rounded-lg bg-primary/10 p-3">
                      <Video className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-medium">
                        {meeting.title || meeting.summary}
                      </h3>
                      <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {new Date(meeting.start).toLocaleDateString()}
                        </span>
                        <span>
                          {new Date(meeting.start).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                          {" - "}
                          {new Date(meeting.end).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                      {meeting.organizer && (
                        <p className="mt-1 text-xs text-muted-foreground">
                          Organizer: {meeting.organizer}
                        </p>
                      )}
                    </div>
                  </div>
                  {meeting.meetLink && (
                    <a
                      href={meeting.meetLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:opacity-90"
                    >
                      <ExternalLink className="h-4 w-4" />
                      Join
                    </a>
                  )}
                </div>
              ))
            ) : (
              <div className="p-12 text-center">
                <Calendar className="mx-auto h-12 w-12 text-muted-foreground" />
                <h3 className="mt-4 font-semibold">No upcoming meetings</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  Your calendar is clear for now
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Join Meeting Dialog */}
        {showJoinDialog && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="w-full max-w-md rounded-lg border bg-card p-6 shadow-lg">
              <h2 className="text-xl font-bold">Join Meeting</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Enter the Google Meet link to join
              </p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="text-sm font-medium">Meeting Link</label>
                  <input
                    type="text"
                    placeholder="https://meet.google.com/xxx-xxxx-xxx"
                    value={meetLink}
                    onChange={(e) => setMeetLink(e.target.value)}
                    className="mt-2 w-full rounded-lg border bg-background px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="autoRecord"
                    checked={autoRecord}
                    onChange={(e) => setAutoRecord(e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300"
                  />
                  <label htmlFor="autoRecord" className="text-sm font-medium">
                    Auto-record meeting
                  </label>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <button
                  onClick={() => setShowJoinDialog(false)}
                  className="flex-1 rounded-lg border px-4 py-2 font-medium hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  onClick={handleJoin}
                  disabled={joinMutation.isPending || !meetLink}
                  className="flex-1 rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground hover:opacity-90 disabled:opacity-50"
                >
                  {joinMutation.isPending ? "Joining..." : "Join"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
