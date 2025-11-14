"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import apiClient from "@/lib/api-client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { formatBytes, formatDuration } from "@/lib/utils"
import { Play, Trash2, Download, FileAudio } from "lucide-react"
import { toast } from "sonner"
import AudioPlayer from "react-audio-player"

export default function RecordingsPage() {
  const [selectedRecording, setSelectedRecording] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ["recordings"],
    queryFn: () => apiClient.getRecordings(),
  })

  const deleteMutation = useMutation({
    mutationFn: (meetingId: string) => apiClient.deleteRecording(meetingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recordings"] })
      toast.success("Recording deleted successfully")
      setSelectedRecording(null)
    },
    onError: () => {
      toast.error("Failed to delete recording")
    },
  })

  const handleDelete = (meetingId: string) => {
    if (confirm(`Are you sure you want to delete recording ${meetingId}?`)) {
      deleteMutation.mutate(meetingId)
    }
  }

  const handlePlay = (meetingId: string) => {
    setSelectedRecording(meetingId)
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <p className="text-lg text-muted-foreground">Loading recordings...</p>
        </div>
      </DashboardLayout>
    )
  }

  const recordings = data?.recordings || []

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Recordings</h1>
          <p className="mt-2 text-muted-foreground">
            Manage and play your meeting recordings
          </p>
        </div>

        {/* Stats */}
        <div className="mb-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-primary/10 p-3">
                <FileAudio className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Recordings</p>
                <p className="text-2xl font-bold">{data?.total || 0}</p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-accent/10 p-3">
                <Download className="h-5 w-5 text-accent" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Size</p>
                <p className="text-2xl font-bold">
                  {formatBytes(
                    recordings.reduce((acc, r) => acc + r.size_mb * 1024 * 1024, 0)
                  )}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-success/10 p-3">
                <Play className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Currently Playing</p>
                <p className="text-lg font-medium">
                  {selectedRecording || "None"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Audio Player */}
        {selectedRecording && (
          <div className="mb-6 rounded-lg border bg-card p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Now Playing</h3>
                <p className="text-sm text-muted-foreground">{selectedRecording}</p>
              </div>
              <button
                onClick={() => setSelectedRecording(null)}
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                Close
              </button>
            </div>
            <AudioPlayer
              src={`${process.env.NEXT_PUBLIC_API_URL}/api/recordings/${selectedRecording}/audio`}
              controls
              className="w-full"
              style={{ width: "100%" }}
            />
          </div>
        )}

        {/* Recordings Table */}
        {recordings.length > 0 ? (
          <div className="rounded-lg border bg-card">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-4 text-left text-sm font-medium">Meeting ID</th>
                    <th className="p-4 text-left text-sm font-medium">Size</th>
                    <th className="p-4 text-left text-sm font-medium">Duration</th>
                    <th className="p-4 text-left text-sm font-medium">Created</th>
                    <th className="p-4 text-left text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recordings.map((recording) => (
                    <tr
                      key={recording.meeting_id}
                      className="border-b last:border-0 hover:bg-muted/30"
                    >
                      <td className="p-4">
                        <p className="font-medium">{recording.meeting_id}</p>
                        <p className="text-xs text-muted-foreground">
                          {recording.format || "WAV"} • {recording.sample_rate || 16000}Hz
                        </p>
                      </td>
                      <td className="p-4 text-sm">
                        {formatBytes(recording.size_mb * 1024 * 1024)}
                      </td>
                      <td className="p-4 text-sm">
                        {recording.duration_seconds
                          ? formatDuration(recording.duration_seconds)
                          : "N/A"}
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">
                        {new Date(recording.created_at).toLocaleDateString()}
                        <br />
                        <span className="text-xs">
                          {new Date(recording.created_at).toLocaleTimeString()}
                        </span>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handlePlay(recording.meeting_id)}
                            className="rounded-lg p-2 text-primary hover:bg-primary/10"
                            title="Play"
                          >
                            <Play className="h-4 w-4" />
                          </button>
                          <a
                            href={`${process.env.NEXT_PUBLIC_API_URL}/api/recordings/${recording.meeting_id}/audio`}
                            download
                            className="rounded-lg p-2 text-accent hover:bg-accent/10"
                            title="Download"
                          >
                            <Download className="h-4 w-4" />
                          </a>
                          <button
                            onClick={() => handleDelete(recording.meeting_id)}
                            className="rounded-lg p-2 text-destructive hover:bg-destructive/10"
                            title="Delete"
                            disabled={deleteMutation.isPending}
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="rounded-lg border bg-card p-12 text-center">
            <FileAudio className="mx-auto h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">No recordings found</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Recordings will appear here after joining meetings
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
