// Meeting Types
export interface Meeting {
  id: string
  title: string
  summary?: string
  start: string
  end?: string
  meetLink: string
  status?: 'scheduled' | 'active' | 'completed'
}

// Recording Types
export interface Recording {
  meeting_id: string
  file_path: string
  size_mb: number
  duration_seconds?: number
  created_at: string
  format?: string
  sample_rate?: number
  channels?: number
}

export interface RecordingsResponse {
  recordings: Recording[]
  total: number
}

// Transcript Types
export interface Transcript {
  meeting_id: string
  transcript: string
  word_count: number
  created_at: string
  file_path?: string
}

export interface TranscriptsResponse {
  transcripts: Transcript[]
  total: number
}

// Meeting Minutes Types
export interface MeetingMinutes {
  meeting_id: string
  meeting_title: string
  meeting_date: string
  attendees?: string[]
  key_points?: string[]
  action_items?: ActionItem[]
  decisions?: string[]
  next_steps?: string[]
  md_file?: string
  json_file?: string
  created_at: string
}

export interface ActionItem {
  task: string
  assignee?: string
  due_date?: string
  priority?: 'high' | 'medium' | 'low'
}

export interface MinutesResponse {
  minutes: MeetingMinutes[]
  total: number
}

// Configuration Types
export interface SystemConfig {
  version: string
  llm: {
    provider: string
    model: string
    available_providers: string[]
  }
  whisper: {
    model: string
    available_models: string[]
  }
  storage: {
    recordings_dir: string
    transcripts_dir: string
    minutes_dir: string
  }
  email: {
    configured: boolean
    smtp_server?: string
    smtp_port?: number
  }
  calendar: {
    enabled: boolean
    monitor_active: boolean
    check_interval_minutes: number
  }
}

export interface CalendarSettings {
  auto_join: boolean
  minutes_before_join: number
  enabled: boolean
}

export interface AISettings {
  provider: 'ollama' | 'llamacpp' | 'azure'
  model: string
}

export interface EmailSettings {
  smtp_server: string
  smtp_port: number
  smtp_user: string
  smtp_password: string
  from_email: string
}

export interface RecordingSettings {
  quality: 'low' | 'medium' | 'high'
  auto_transcribe: boolean
  sample_rate: number
}

// API Request/Response Types
export interface JoinMeetingRequest {
  meetLink: string
  meetingId?: string
  autoRecord?: boolean
}

export interface JoinMeetingResponse {
  status: string
  meetingId: string
  recordingPath?: string
  message: string
}

export interface EmailRequest {
  recipients: string[]
  subject?: string
  include_attachment?: boolean
}

export interface EmailResponse {
  status: string
  message: string
  recipients: string[]
  meeting_id: string
}

// Dashboard Types
export interface DashboardStats {
  total_meetings: number
  active_meetings: number
  scheduled_meetings: number
  total_hours: number
  total_recordings: number
  total_transcripts: number
  total_minutes: number
}

// WebSocket Types
export interface MeetingStatusUpdate {
  meeting_id: string
  status: 'joining' | 'active' | 'recording' | 'ended'
  timestamp: string
  message?: string
}

// Auth Types
export interface User {
  id: string
  email: string
  name?: string
  role?: 'admin' | 'user'
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}
