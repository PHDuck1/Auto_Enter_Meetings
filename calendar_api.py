import os.path
import re
import webbrowser
import threading
import pygetwindow
import time
import pyautogui

from datetime import datetime
from recording import OBSManager

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

PATH_TO_CREDS = 'credentials.json'

CALENDAR_ID = 'd5d83e80aad7690af4de8b70dac31650c55680bec3d5494b7b06a0205e7119ca@group.calendar.google.com'


class CalendarProcessor:

    def __init__(self, record_needed: bool = False):
        self.record_needed = record_needed
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
                    PATH_TO_CREDS, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    @staticmethod
    def get_link(desc: str):
        """ parse information about meetings, return link to zoom or google meet meeting """

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

        event_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time,
            maxResults=1, singleEvents=True,
            orderBy='startTime').execute()

        event = event_result.get('items', [])

        if event:
            event = event[0]

            name = event['summary']
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            link = self.get_link(event.get('description', ''))

            meeting = Meet(name, start, end, link, self.record_needed, wait=True)

            return meeting


class Meet:
    def __init__(self, name: str, start_time: str, end_time: str, link: str, record_needed: bool = False,
                 wait: bool = True):
        if record_needed:
            self.manager = OBSManager()
        self.name = name
        self.start_time = self._parse_time(start_time)
        self.end_time = self._parse_time(end_time)
        self.link = link
        self.record_needed = record_needed
        self.wait = wait

    def __str__(self):
        return f'{self.name}:\nstarting at: {self.start_time},\nending at: {self.end_time},\nlink: {self.link}'

    @staticmethod
    def _parse_time(time_str: str) -> datetime:
        formatted_time = datetime.strptime(time_str[:-6], '%Y-%m-%dT%H:%M:%S')
        return formatted_time

    @staticmethod
    def seconds_to_hours_min_sec(seconds: int):
        hours_left = seconds // 3600
        minutes_left = seconds % 3600 // 60
        seconds_left = seconds % 60
        return hours_left, minutes_left, seconds_left

    def enter(self):
        if not self.link:
            print('No link in upcoming meeting')
            return

        # Check if the Zoom Meeting window is open
        if pygetwindow.getWindowsWithTitle('Zoom Meeting'):
            print('Zoom Meeting window is open. Canceling enter')
        else:
            webbrowser.open(self.link)
            print("Meeting opened.")

        # Check if recording is going
        if self.record_needed:
            # if not self.manager.is_recording():
            self.manager.set_scene('ZoomRec')
            self.manager.start_recording()

    def wait_and_enter(self):
        time_left = self.start_time - datetime.now()
        if time_left.total_seconds() <= 0:
            self.enter()
            return

        # Calculate the time left until the meeting starts
        hours_left, minutes_left, seconds_left = self.seconds_to_hours_min_sec(time_left.seconds)

        if hours_left >= 1:
            print(f"{self.name} will start in {int(hours_left)} hours and {int(minutes_left)} minutes.")
        else:
            print(f"{self.name} will start in {int(minutes_left)} minutes and {int(seconds_left)} seconds.")

        # Wait until the meeting starts or the Zoom Meeting window is opened
        while time_left.total_seconds() > 0:
            time_left = self.start_time - datetime.now()
            time.sleep(5)

        self.enter()

        # Start a timer for the duration of the meeting
        duration = (self.end_time - self.start_time).total_seconds()
        timer = threading.Timer(duration, self.close_zoom_window)
        timer.start()
        print('Timer to close window set')

    def close_zoom_window(self):
        """Closes window with title 'Zoom Meeting' and stops recording if it goes"""
        # Wait for 5 minutes after the meeting ends
        if self.wait:
            time.sleep(5 * 60)

        # Stop recording
        if self.record_needed:
            self.manager.stop_recording()
            print('Recording stopped')

        # Find the Zoom Meeting window and close it
        zoom_window = pygetwindow.getWindowsWithTitle('Zoom Meeting')
        if zoom_window:
            zoom_window = zoom_window[0]
            zoom_window.close()
            zoom_window.activate()

            time.sleep(0.5)
            pyautogui.press('enter')
            print('Window closed')

        else:
            print('Window is not open')


if __name__ == '__main__':
    calendar = CalendarProcessor(record_needed=True)
    print(calendar.meet)
    calendar.meet.wait_and_enter()
