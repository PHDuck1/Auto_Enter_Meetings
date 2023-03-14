import time

import obsws_python as obs
import obsws_python.error as errors


class OBSManager:
    DEFAULT_NAME_PATTERN = '%MM_%DD_%hh'

    def __init__(self):
        # Connect to obs websocket using creds provided in config.toml
        self.client = obs.ReqClient()

    def set_scene(self, scene_name: str = 'ZoomRec') -> bool:
        """Sets current program scene to provided name"""
        try:
            self.client.set_current_program_scene(scene_name)
            return True

        except errors.OBSSDKError:
            print('You are trying to switch to not existing scene.')
            return False

    def start_recording(self, name: str = '') -> None:
        """Set up a filename for output file"""

        # set up a name or pattern for recording file
        if name:
            self.client.set_profile_parameter("Output", "FilenameFormatting", name)
        else:
            self.client.set_profile_parameter("Output", "FilenameFormatting", self.DEFAULT_NAME_PATTERN)

        # start recording
        self.client.start_record()

    def stop_recording(self) -> str:
        """stops recording and returns path to output file"""

        res = self.client.stop_record()
        return res.output_path

    def is_recording(self) -> bool:
        res = self.client.get_record_status()
        return res.output_active


def main():
    manager = OBSManager()
    manager.set_scene('ZoomRec')
    manager.start_recording()
    time.sleep(5)
    manager.stop_recording()


if __name__ == '__main__':
    main()
