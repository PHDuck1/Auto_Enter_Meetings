import os.path
import re
import webbrowser

from datetime import datetime
from time import sleep

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarProcessor:
    meet = {}

    def __init__(self):
        self.meet = self.get_next_meeting()

    @staticmethod
    def _get_creds():
        creds = None

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

    @staticmethod
    def get_link(desc: str):
        """ parse information about meetings, return link to zoom or google self.meet meeting """

        match = re.search(r'https://[-a-zA-Z\d()@:%_+.~#?&/=]*', desc)

        if match:
            return match.group(0)

    def get_next_meeting(self):
        """ return meet object with name, date of start and link """
        try:
            service = build('calendar', 'v3', credentials=self._get_creds())
        except:
            os.remove('token.json')
            service = build('calendar', 'v3', credentials=self._get_creds())

        now = datetime.utcnow()
        start_time = now.isoformat() + 'Z'

        event_result = service.events().list(calendarId='primary', timeMin=start_time,
                                             maxResults=1, singleEvents=True,
                                             orderBy='startTime').execute()

        event = event_result.get('items', [])

        if event:
            event = event[0]

            meeting = {
                'name': event['summary'],
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'link': self.get_link(event.get('description', ''))
            }
            return meeting

    def open_link(self):

        link = self.meet.get('link', None)
        if link:
            webbrowser.open(link)
        else:
            print('No link in meeting')

    def enter_meet(self):
        """ enter next meeting """
        if self.meet:
            # parse date from calendar
            start_time = datetime.strptime(self.meet['start'][:-6], '%Y-%m-%dT%H:%M:%S')
            print(f'Entering {self.meet["name"]} at {start_time:%H:%M} \n{self.meet["link"]}')
            wait = start_time - datetime.now()
            print(f'Time left: {str(wait)[:-7]}')
            sleep(wait.seconds - 30)
            self.open_link()
            print('Entered')
        else:
            print('No upcoming meetings')


if __name__ == '__main__':
    calendar = CalendarProcessor()
    calendar.enter_meet()
