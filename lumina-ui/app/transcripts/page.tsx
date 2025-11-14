"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import apiClient from "@/lib/api-client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Search, FileText, Download, Eye } from "lucide-react"

export default function TranscriptsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTranscript, setSelectedTranscript] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ["transcripts"],
    queryFn: () => apiClient.getTranscripts(),
  })

  const { data: transcriptContent } = useQuery({
    queryKey: ["transcript", selectedTranscript],
    queryFn: () => apiClient.getTranscript(selectedTranscript!),
    enabled: !!selectedTranscript,
  })

  const transcripts = data?.transcripts || []
  const filteredTranscripts = transcripts.filter((t) =>
    t.meeting_id.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <p className="text-lg text-muted-foreground">Loading transcripts...</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Transcripts</h1>
          <p className="mt-2 text-muted-foreground">
            Search and view meeting transcripts
          </p>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search transcripts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border bg-background py-2 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Transcripts List */}
          <div className="lg:col-span-1">
            <div className="rounded-lg border bg-card">
              <div className="border-b p-4">
                <h2 className="font-semibold">All Transcripts ({filteredTranscripts.length})</h2>
              </div>
              <div className="max-h-[600px] overflow-y-auto">
                {filteredTranscripts.length > 0 ? (
                  filteredTranscripts.map((transcript) => (
                    <button
                      key={transcript.meeting_id}
                      onClick={() => setSelectedTranscript(transcript.meeting_id)}
                      className={`w-full border-b p-4 text-left transition-colors last:border-0 hover:bg-muted/50 ${
                        selectedTranscript === transcript.meeting_id
                          ? "bg-primary/10"
                          : ""
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <FileText className="mt-1 h-5 w-5 flex-shrink-0 text-primary" />
                        <div className="flex-1 overflow-hidden">
                          <p className="truncate font-medium">
                            {transcript.meeting_id}
                          </p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {transcript.word_count || 0} words
                          </p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {new Date(transcript.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="p-8 text-center">
                    <p className="text-sm text-muted-foreground">
                      No transcripts found
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Transcript Viewer */}
          <div className="lg:col-span-2">
            {selectedTranscript && transcriptContent ? (
              <div className="rounded-lg border bg-card">
                <div className="flex items-center justify-between border-b p-4">
                  <div>
                    <h2 className="font-semibold">{selectedTranscript}</h2>
                    <p className="text-sm text-muted-foreground">
                      {transcriptContent.text?.split(" ").length || 0} words
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button className="rounded-lg p-2 text-accent hover:bg-accent/10">
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <div className="max-h-[600px] overflow-y-auto p-6">
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    {transcriptContent.text ? (
                      <p className="whitespace-pre-wrap leading-relaxed">
                        {transcriptContent.text}
                      </p>
                    ) : transcriptContent.segments ? (
                      <div className="space-y-4">
                        {transcriptContent.segments.map((segment: any, idx: number) => (
                          <div key={idx} className="flex gap-4">
                            <span className="text-xs text-muted-foreground">
                              [{Math.floor(segment.start / 60)}:
                              {String(Math.floor(segment.start % 60)).padStart(2, "0")}]
                            </span>
                            <p className="flex-1">{segment.text}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-muted-foreground">No transcript content available</p>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex h-full min-h-[400px] items-center justify-center rounded-lg border bg-card">
                <div className="text-center">
                  <Eye className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-4 font-semibold">No transcript selected</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Select a transcript from the list to view its content
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
