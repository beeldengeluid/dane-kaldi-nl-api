import logging
import os
from base_util import run_shell_command


"""
This class supplies the function for transcoding valid video files into mp3 format (i.e. valid input for Kaldi)
"""
class Transcoder(object):

    def __init__(self, config):
        self.logger = logging.getLogger(config["LOG_NAME"])

    def transcode_to_mp3(self, path: str, asr_path: str) -> bool:
        self.logger.debug(f"Encoding file: {path}")
        cmd = "ffmpeg -i {0} {1}".format(path, asr_path)
        return run_shell_command(cmd, self.logger)

    def get_transcode_output_path(self, input_path: str, asset_id: str) -> str:
        return os.path.join(
            os.sep,
            os.path.dirname(input_path),  # the dir the input file is in
            asset_id + ".mp3",  # same name as input file, but with mp3 extension
        )
