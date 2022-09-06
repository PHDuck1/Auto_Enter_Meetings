from datetime import datetime

import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarProcessor:

    def _get_creds(self):
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return creds

    def get_link(self, desc: str):
        """ parse information about meetings, return link to zoom or google meet meeting """

        match = re.search('https:\/\/[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*', desc)

        if match:
            return match.group(0)
    
    def get_next_meetings(self, n: int=1):
        """ return links to next n meetings """

        service = build('calendar', 'v3', credentials=self._get_creds())
        now = datetime.utcnow().isoformat() + 'Z'

        # get n upcoming events
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=n, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        # return list of tuples with name, start time and link to meeting
        if events:
            res = []
            for event in events:
                name = event['summary']
                start = event['start'].get('dateTime', event['start'].get('date'))
                desc = event.get('description', '')
                link = self.get_link(desc)
                res.append((name, start, link))
            return res

    def get_current_meeting(self):
        """ return link to meetings which is going on right now """

        return 'meet'
    
