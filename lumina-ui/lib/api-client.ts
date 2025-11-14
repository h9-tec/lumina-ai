import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type {
  Meeting,
  RecordingsResponse,
  Recording,
  TranscriptsResponse,
  Transcript,
  MinutesResponse,
  MeetingMinutes,
  SystemConfig,
  JoinMeetingRequest,
  JoinMeetingResponse,
  EmailRequest,
  EmailResponse,
} from '@/types'

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
      }
      return config
    })

    // Handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Clear token and redirect to login
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token')
            window.location.href = '/auth/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // Meetings API
  async joinMeeting(data: JoinMeetingRequest): Promise<JoinMeetingResponse> {
    const response = await this.client.post<JoinMeetingResponse>('/join-meeting/', data)
    return response.data
  }

  async getUpcomingMeetings(params?: {
    max_results?: number
    time_min?: string
    time_max?: string
  }): Promise<{ meetings: Meeting[]; total: number }> {
    const response = await this.client.get('/calendar/upcoming-meetings/', { params })
    return response.data
  }

  async startCalendarMonitor(): Promise<{ status: string; message: string }> {
    const response = await this.client.post('/calendar/start-monitor/')
    return response.data
  }

  async stopCalendarMonitor(): Promise<{ status: string; message: string }> {
    const response = await this.client.post('/calendar/stop-monitor/')
    return response.data
  }

  async getStatus(): Promise<{
    status: string
    calendar_monitor_active: boolean
    active_meetings: number
    uptime: string
    version: string
  }> {
    const response = await this.client.get('/status/')
    return response.data
  }

  // Recordings API
  async getRecordings(): Promise<RecordingsResponse> {
    const response = await this.client.get<RecordingsResponse>('/api/recordings/')
    return response.data
  }

  async getRecording(meetingId: string): Promise<Recording> {
    const response = await this.client.get<Recording>(`/api/recordings/${meetingId}`)
    return response.data
  }

  async deleteRecording(meetingId: string): Promise<{ status: string; message: string }> {
    const response = await this.client.delete(`/api/recordings/${meetingId}`)
    return response.data
  }

  // Transcripts API
  async transcribeRecording(
    meetingId: string,
    model: string = 'base'
  ): Promise<{ status: string; message: string }> {
    const response = await this.client.post(`/api/transcripts/transcribe/${meetingId}`, null, {
      params: { model },
    })
    return response.data
  }

  async getTranscripts(): Promise<TranscriptsResponse> {
    const response = await this.client.get<TranscriptsResponse>('/api/transcripts/')
    return response.data
  }

  async getTranscript(meetingId: string): Promise<Transcript> {
    const response = await this.client.get<Transcript>(`/api/transcripts/${meetingId}`)
    return response.data
  }

  // Meeting Minutes API
  async generateMinutes(
    meetingId: string,
    provider: string = 'ollama',
    model: string = 'llama3'
  ): Promise<{ status: string; message: string }> {
    const response = await this.client.post(`/api/minutes/generate/${meetingId}`, null, {
      params: { provider, model },
    })
    return response.data
  }

  async getAllMinutes(): Promise<MinutesResponse> {
    const response = await this.client.get<MinutesResponse>('/api/minutes/')
    return response.data
  }

  async getMinutes(
    meetingId: string,
    format: 'markdown' | 'json' = 'markdown'
  ): Promise<{ meeting_id: string; format: string; content: any }> {
    const response = await this.client.get(`/api/minutes/${meetingId}`, {
      params: { format },
    })
    return response.data
  }

  async emailMinutes(meetingId: string, data: EmailRequest): Promise<EmailResponse> {
    const response = await this.client.post<EmailResponse>(
      `/api/minutes/email/${meetingId}`,
      data
    )
    return response.data
  }

  async processComplete(
    meetingId: string,
    params?: {
      skip_transcribe?: boolean
      skip_minutes?: boolean
      skip_email?: boolean
      provider?: string
      model?: string
      recipients?: string
    }
  ): Promise<{ status: string; message: string; steps: string[] }> {
    const response = await this.client.post(`/api/minutes/process/${meetingId}`, null, {
      params,
    })
    return response.data
  }

  // Configuration API
  async getConfig(): Promise<SystemConfig> {
    const response = await this.client.get<SystemConfig>('/api/config/')
    return response.data
  }

  async updateConfig(config: Partial<SystemConfig>): Promise<{ status: string; message: string }> {
    const response = await this.client.post('/api/config/', config)
    return response.data
  }
}

// Export singleton instance
const apiClient = new APIClient()
export default apiClient
