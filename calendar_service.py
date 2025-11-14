from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Calendar API using OAuth2"""
        # Token file stores the user's access and refresh tokens
        token_path = 'token.pickle'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Look for credentials file
                credentials_file = None
                possible_names = [
                    'credentials.json',
                    'client_secret_966764886522-8ch0p4ln423ktj2eb9c08s5p15eigr8g.apps.googleusercontent.com.json'
                ]

                for name in possible_names:
                    if os.path.exists(name):
                        credentials_file = name
                        break

                if not credentials_file:
                    raise FileNotFoundError(
                        "Google credentials file not found. Please download it from Google Cloud Console.\n"
                        "Visit: https://console.cloud.google.com/apis/credentials"
                    )

                print(f"Using credentials file: {credentials_file}")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)
        print("Successfully authenticated with Google Calendar")

    def get_upcoming_meetings(self, minutes_ahead: int = 5, max_results: int = 10) -> List[Dict]:
        """
        Get upcoming Google Meet meetings from calendar

        Args:
            minutes_ahead: How many minutes ahead to look for meetings
            max_results: Maximum number of events to return

        Returns:
            List of meeting dictionaries with link, title, start time, etc.
        """
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(minutes=minutes_ahead)).isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            meetings = []

            for event in events:
                # Check if event has a Google Meet link
                meet_link = None

                # Check in hangoutLink (newer format)
                if 'hangoutLink' in event:
                    meet_link = event['hangoutLink']

                # Check in conferenceData (newer format)
                elif 'conferenceData' in event:
                    entry_points = event['conferenceData'].get('entryPoints', [])
                    for entry in entry_points:
                        if entry.get('entryPointType') == 'video':
                            meet_link = entry.get('uri')
                            break

                # Check in description or location
                elif 'description' in event and 'meet.google.com' in event['description']:
                    # Extract meet link from description
                    import re
                    match = re.search(r'https://meet\.google\.com/[a-z-]+', event['description'])
                    if match:
                        meet_link = match.group(0)

                if meet_link:
                    meeting = {
                        'id': event.get('id'),
                        'title': event.get('summary', 'Untitled Meeting'),
                        'meet_link': meet_link,
                        'start_time': event['start'].get('dateTime', event['start'].get('date')),
                        'end_time': event['end'].get('dateTime', event['end'].get('date')),
                        'description': event.get('description', ''),
                        'attendees': event.get('attendees', [])
                    }
                    meetings.append(meeting)

            return meetings

        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []

    def get_meeting_starting_now(self, tolerance_minutes: int = 2) -> Dict:
        """
        Get a meeting that is starting right now (within tolerance)

        Args:
            tolerance_minutes: Time tolerance in minutes (before and after)

        Returns:
            Meeting dictionary or None
        """
        meetings = self.get_upcoming_meetings(minutes_ahead=tolerance_minutes)

        if not meetings:
            return None

        # Return the first meeting (closest to current time)
        return meetings[0] if meetings else None

    def list_todays_meetings(self) -> List[Dict]:
        """Get all meetings for today"""
        now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=1)).isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            meetings = []

            for event in events:
                meeting = {
                    'title': event.get('summary', 'Untitled'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'has_meet': 'hangoutLink' in event or 'conferenceData' in event
                }
                meetings.append(meeting)

            return meetings

        except Exception as e:
            print(f"Error fetching today's meetings: {e}")
            return []


if __name__ == "__main__":
    # Test the calendar service
    cal = CalendarService()

    print("\n=== Today's Meetings ===")
    meetings = cal.list_todays_meetings()
    for meeting in meetings:
        print(f"- {meeting['title']} at {meeting['start']} (Meet: {meeting['has_meet']})")

    print("\n=== Upcoming Google Meet Links ===")
    upcoming = cal.get_upcoming_meetings(minutes_ahead=1440)  # Next 24 hours
    for meeting in upcoming:
        print(f"- {meeting['title']}")
        print(f"  Link: {meeting['meet_link']}")
        print(f"  Time: {meeting['start_time']}")
