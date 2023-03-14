import time
import unittest
import pygetwindow
from datetime import datetime, timedelta
from calendar_api import Meet


class TestMeet(unittest.TestCase):
    def setUp(self):
        self.meet = Meet('Test Meeting', '2023-03-15T10:00:00-07:00', '2023-03-15T11:00:00-07:00',
                         'https://us04web.zoom.us/j/78392111794?pwd=TqguGao3JBMTl46bpLrISpfb61zKOD.1',
                         record_needed=True, wait=False)

    def test_parse_time(self):
        time_str = '2023-03-15T10:00:00-07:00'
        expected_time = datetime(2023, 3, 15, 10, 0, 0)
        self.assertEqual(self.meet._parse_time(time_str), expected_time)

    def test_seconds_to_hours_min_sec(self):
        seconds = 3800
        expected_result = (1, 3, 20)
        self.assertEqual(self.meet.seconds_to_hours_min_sec(seconds), expected_result)

    def test_enter_meeting(self):
        # Zoom Meeting window must not be open and recording must be off
        self.assertEqual(pygetwindow.getWindowsWithTitle('Zoom Meeting'), [])
        self.assertFalse(self.meet.manager.is_recording())

        self.meet.enter()
        time.sleep(15)

        # After entering window 'Zoom Meeting' must be opened and recording has to go
        self.assertNotEqual(pygetwindow.getWindowsWithTitle('Zoom Meeting'), [])
        self.assertTrue(self.meet.manager.is_recording())

        self.meet.manager.stop_recording()
        self.meet.close_zoom_window()
        time.sleep(15)

    def test_wait_and_enter_meeting(self):
        # Zoom Meeting window must not be open and recording must be off too
        self.assertEqual(pygetwindow.getWindowsWithTitle('Zoom Meeting'), [])
        self.assertFalse(self.meet.manager.is_recording())

        # setup right start time
        self.meet.start_time = datetime.now() + timedelta(seconds=15)
        self.meet.end_time = datetime.now() + timedelta(seconds=40)

        self.meet.wait_and_enter()
        time.sleep(15)

        # After entering window 'Zoom Meeting' must be opened and recording has to go
        self.assertNotEqual(pygetwindow.getWindowsWithTitle('Zoom Meeting'), [])
        self.assertTrue(self.meet.manager.is_recording())

        # after passing timer till the end of the meeting window must be closed and recording turned off
        time.sleep(60)
        self.assertEqual(pygetwindow.getWindowsWithTitle('Zoom Meeting'), [])
        self.assertFalse(self.meet.manager.is_recording())


if __name__ == '__main__':
    unittest.main()
