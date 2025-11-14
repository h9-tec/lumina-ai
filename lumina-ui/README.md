# Lumina AI - Frontend Dashboard

Modern, professional web dashboard for Lumina AI meeting intelligence platform built with Next.js 15, React 19, TypeScript, Tailwind CSS, and Shadcn UI.

## 🎯 Features

- ✅ **Real-time Dashboard** - Live meeting status and statistics
- ✅ **Meeting Management** - View upcoming meetings from Google Calendar
- ✅ **Recording Library** - Browse, play, and delete meeting recordings
- ✅ **Transcript Viewer** - Search and view meeting transcripts
- ✅ **Meeting Minutes** - AI-generated summaries with action items
- ✅ **Configuration Panel** - No-code settings for non-technical users
- ✅ **Dark/Light Mode** - Automatic theme switching
- ✅ **Responsive Design** - Mobile, tablet, and desktop support
- ✅ **Type-Safe API** - Full TypeScript integration with FastAPI backend

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Lumina AI backend running on `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd lumina-ui

# Install dependencies
npm install
# or
yarn install
# or
pnpm install

# Start development server
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📁 Project Structure

```
lumina-ui/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout with providers
│   ├── page.tsx                 # Home page (redirects to dashboard)
│   ├── providers.tsx            # React Query & Theme providers
│   ├── globals.css              # Global styles with Tailwind
│   └── dashboard/
│       └── page.tsx             # Main dashboard page
│
├── components/                   # React components
│   ├── ui/                      # Shadcn UI components
│   ├── dashboard/               # Dashboard-specific components
│   ├── meetings/                # Meeting-related components
│   └── settings/                # Settings/config components
│
├── lib/                         # Utilities and libraries
│   ├── api-client.ts            # Axios client for FastAPI
│   ├── utils.ts                 # Helper functions (cn, formatters)
│   └── auth.ts                  # Authentication utilities (TBD)
│
├── hooks/                       # Custom React hooks
│   ├── use-meetings.ts          # Meeting data hooks (TBD)
│   ├── use-recordings.ts        # Recording data hooks (TBD)
│   └── use-config.ts            # Config data hooks (TBD)
│
├── types/                       # TypeScript type definitions
│   └── index.ts                 # All API types and interfaces
│
├── public/                      # Static assets
│
├── .env.local                   # Environment variables
├── package.json                 # Dependencies and scripts
├── tsconfig.json                # TypeScript configuration
├── tailwind.config.ts           # Tailwind CSS configuration
├── postcss.config.js            # PostCSS configuration
└── next.config.js               # Next.js configuration
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket URL for real-time updates
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# App Configuration
NEXT_PUBLIC_APP_NAME=Lumina AI
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 📚 API Integration

The frontend integrates with the Lumina AI FastAPI backend through the `api-client.ts` module.

### Example Usage

```typescript
import apiClient from '@/lib/api-client'

// Get upcoming meetings
const meetings = await apiClient.getUpcomingMeetings()

// Join a meeting
const result = await apiClient.joinMeeting({
  meetLink: 'https://meet.google.com/xxx-xxxx-xxx',
  autoRecord: true
})

// Get recordings
const recordings = await apiClient.getRecordings()

// Transcribe recording
await apiClient.transcribeRecording('20251114_194510', 'base')

// Generate meeting minutes
await apiClient.generateMinutes('20251114_194510', 'ollama', 'llama3')
```

### Available API Methods

**Meetings**
- `joinMeeting(data)` - Join a Google Meet session
- `getUpcomingMeetings(params)` - Get calendar meetings
- `startCalendarMonitor()` - Start automatic monitoring
- `stopCalendarMonitor()` - Stop monitoring
- `getStatus()` - Get system status

**Recordings**
- `getRecordings()` - List all recordings
- `getRecording(meetingId)` - Get recording details
- `deleteRecording(meetingId)` - Delete a recording

**Transcripts**
- `transcribeRecording(meetingId, model)` - Start transcription
- `getTranscripts()` - List all transcripts
- `getTranscript(meetingId)` - Get transcript content

**Meeting Minutes**
- `generateMinutes(meetingId, provider, model)` - Generate minutes
- `getAllMinutes()` - List all minutes
- `getMinutes(meetingId, format)` - Get minutes (markdown/json)
- `emailMinutes(meetingId, data)` - Send minutes via email
- `processComplete(meetingId, params)` - Full pipeline

**Configuration**
- `getConfig()` - Get system configuration
- `updateConfig(config)` - Update settings

## 🎨 UI Components

This project uses [Shadcn UI](https://ui.shadcn.com/) components built with Radix UI and Tailwind CSS.

### Adding New Components

```bash
# Install Shadcn CLI (if not already installed)
npx shadcn-ui@latest init

# Add components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add table
# ... etc
```

### Available Components

The following Shadcn components are configured and ready to use:

- Button, Card, Dialog, Dropdown Menu
- Input, Label, Select, Switch
- Table, Tabs, Toast, Tooltip
- Avatar, Alert Dialog, Checkbox
- Popover, Scroll Area, Separator
- Calendar, Command (search)

## 📝 Development Guide

### Pages to Implement

Based on the todo list, here are the remaining pages to build:

1. **Recordings Page** (`app/recordings/page.tsx`)
   - List view with audio player
   - Delete functionality
   - File size and duration display

2. **Transcripts Page** (`app/transcripts/page.tsx`)
   - Search and filter transcripts
   - Word count and timestamp display
   - Export functionality

3. **Minutes Page** (`app/minutes/page.tsx`)
   - Markdown viewer for meeting minutes
   - Action items list
   - Download as MD/JSON

4. **Settings Page** (`app/settings/page.tsx`)
   - No-code configuration panel
   - Calendar settings (auto-join toggle)
   - AI model selection
   - Email configuration
   - Recording quality settings

5. **Analytics Page** (`app/analytics/page.tsx`)
   - Charts for meetings over time
   - Duration statistics
   - Usage metrics

### Custom Hooks Pattern

Create reusable hooks for data fetching:

```typescript
// hooks/use-recordings.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'

export function useRecordings() {
  return useQuery({
    queryKey: ['recordings'],
    queryFn: () => apiClient.getRecordings()
  })
}

export function useDeleteRecording() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (meetingId: string) => apiClient.deleteRecording(meetingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recordings'] })
    }
  })
}
```

### State Management

This project uses:
- **React Query** for server state
- **Zustand** for client state (if needed)
- **next-themes** for theme state

Example Zustand store:

```typescript
// lib/stores/use-app-store.ts
import { create } from 'zustand'

interface AppState {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open })
}))
```

## 🎯 Next Steps

### Phase 1: Core Pages (Week 1-2)
- [ ] Complete recordings page with audio player
- [ ] Build transcripts viewer with search
- [ ] Create meeting minutes display
- [ ] Add navigation sidebar

### Phase 2: Configuration (Week 3)
- [ ] Build no-code settings panel
- [ ] Implement calendar settings
- [ ] Add AI model configuration
- [ ] Create email settings form

### Phase 3: Advanced Features (Week 4)
- [ ] WebSocket integration for real-time updates
- [ ] Analytics dashboard with charts
- [ ] Manual meeting join interface
- [ ] Authentication system

### Phase 4: Polish (Week 5-6)
- [ ] Dark/light theme refinement
- [ ] Mobile responsiveness
- [ ] Accessibility improvements
- [ ] Loading states and skeletons
- [ ] Error handling and toasts
- [ ] User documentation

## 🔐 Authentication

Authentication system needs to be implemented. Planned approach:

1. JWT tokens stored in localStorage
2. Protected routes with middleware
3. Login/logout pages
4. Token refresh mechanism

Example middleware:

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')

  if (!token && !request.nextUrl.pathname.startsWith('/auth')) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/recordings/:path*', '/settings/:path*']
}
```

## 📦 Build & Deploy

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm run start
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Build application
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

Build and run:

```bash
docker build -t lumina-ui .
docker run -p 3000:3000 lumina-ui
```

### Environment-Specific Builds

```bash
# Development
npm run dev

# Staging
NEXT_PUBLIC_API_URL=https://staging-api.lumina.ai npm run build

# Production
NEXT_PUBLIC_API_URL=https://api.lumina.ai npm run build
```

## 🧪 Testing

Add testing libraries:

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom
```

Example test:

```typescript
// __tests__/dashboard.test.tsx
import { render, screen } from '@testing-library/react'
import DashboardPage from '@/app/dashboard/page'

describe('Dashboard', () => {
  it('renders dashboard heading', () => {
    render(<DashboardPage />)
    expect(screen.getByText('Lumina AI Dashboard')).toBeInTheDocument()
  })
})
```

## 🐛 Troubleshooting

### Common Issues

**Issue:** API calls fail with CORS errors
**Solution:** Ensure FastAPI backend has CORS middleware configured

**Issue:** WebSocket connection fails
**Solution:** Check `NEXT_PUBLIC_WS_URL` in `.env.local`

**Issue:** Dark mode not persisting
**Solution:** Check browser localStorage is enabled

**Issue:** Build errors with TypeScript
**Solution:** Run `npm run lint` and fix type errors

## 📄 License

This project is part of the Lumina AI ecosystem.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests if applicable
4. Submit a pull request

## 📧 Support

For issues and questions, visit: [https://github.com/h9-tec/lumina-ai/issues](https://github.com/h9-tec/lumina-ai/issues)

---

**Built with** Next.js • React • TypeScript • Tailwind CSS • Shadcn UI
