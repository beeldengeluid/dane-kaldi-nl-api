import os
import ntpath
import shutil
import logging
import json
import time
from api_util import APIResponse
from asr import ASR
from transcode import Transcoder


"""
This module contains all the specific processing functions for the DANE-asr-worker. The reason
to separate it from worker.py is so it can also be called via the server.py (debugging UI)

The processing consists of:
- validating the input file (provided by the download worker)
- if it is an audio file: simply run ASR (see module: asr.py)
- if not: first transcode it (see module: transcode.py)
- finally: package the ASR output into a tar.gz (optional)
"""


class WorkProcessor(object):
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(config["LOG_NAME"])
        self.asr = ASR(config)
        self.transcoder = Transcoder(self.config)

    # simulates running ASR and/or transcoding, so the API communication can be tested in isolation
    def run_simulation(self, pid, input_file_path, asynchronous=False):
        self.logger.debug(
            "simlating ASR, but verifying the validity of the request params"
        )
        self.logger.debug(input_file_path)

        # first write to the PID that the process is busy, then sleep for 5 seconds to simulate ASR/transcoding
        self._write_pid_file_json(pid, APIResponse.SIMULATION_IN_PROGRESS.value)
        if not os.path.isfile(input_file_path):  # check if inputfile exists
            return self._resp_to_pid_file(pid, asynchronous, APIResponse.FILE_NOT_FOUND)
        else:
            time.sleep(5)
            return self._resp_to_pid_file(pid, asynchronous, APIResponse.ASR_SUCCESS)

    # processes the input and keeps a PID file with status information in asynchronous mode
    def process_input_file(self, pid, input_file_path, asynchronous=False):
        self.logger.debug("processing {} for PID={}".format(input_file_path, pid))

        if not os.path.isfile(input_file_path):  # check if inputfile exists
            return self._resp_to_pid_file(pid, asynchronous, APIResponse.FILE_NOT_FOUND)

        # extract the asset_id, i.e. filename without the path, and the file extension
        asset_id, extension = self._get_asset_info(input_file_path)

        # check if the file needs to be transcoded and possibly obtain a new asr_input_path
        try:
            asr_input_path = self._try_transcode(input_file_path, asset_id, extension)
        except ValueError as e:
            return self._resp_to_pid_file(pid, asynchronous, APIResponse[str(e)])

        # run the ASR
        try:
            self.asr.run_asr(asr_input_path, asset_id)
        except Exception as e:
            print(e)
            return self._resp_to_pid_file(pid, asynchronous, APIResponse.ASR_FAILED)

        # finally process the ASR results and return the status message
        return self._resp_to_pid_file(
            pid, asynchronous, self.asr.process_asr_output(asset_id)
        )

    def poll_pid_status(self, pid):
        self.logger.debug("Getting status for pid {}".format(pid))
        if not self._pid_file_exists(pid):
            return APIResponse.PID_NOT_FOUND.value

        status = self._read_pid_file(pid)
        try:
            return json.loads(status)
        except Exception:
            return APIResponse.PID_FILE_CORRUPTED.value

    def _try_transcode(self, asr_input_path, asset_id, extension):
        if not self._is_audio_file(extension):

            if not self._is_transcodable(extension):
                raise ValueError(APIResponse.ASR_INPUT_UNACCEPTABLE.name)

            transcoding_output_path = self.transcoder.get_transcode_output_path(
                asr_input_path, asset_id
            )

            success = self.transcoder.transcode_to_mp3(
                asr_input_path,
                transcoding_output_path,
            )
            if success is False:
                raise ValueError(APIResponse.TRANSCODE_FAILED.name)

            return (
                transcoding_output_path  # the transcode output is the input for the ASR
            )
        return asr_input_path

    def _get_asset_info(self, file_path):
        # grab the file_name from the path
        file_name = ntpath.basename(file_path)

        # split up the file in asset_id (used for creating a subfolder in the output) and extension
        asset_id, extension = os.path.splitext(file_name)

        return asset_id, extension

    def _is_audio_file(self, extension):
        return extension in [".mp3", ".wav"]

    def _is_transcodable(self, extension):
        return extension in [".mov", ".mp4", ".m4a", ".3gp", ".3g2", ".mj2"]

    # clean up input files
    def _remove_files(self, path):
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete {0}. Reason: {1}".format(file_path, e))

    """-------------------------------------- PID FILE FUNCTIONS -----------------------------------------------"""

    # writes the API response to the PID file, if the "ASR job" is running asynchronously
    def _resp_to_pid_file(self, pid: str, asynchronous: bool, resp: APIResponse):
        self.logger.debug(resp.value)
        if asynchronous:
            self._write_pid_file_json(pid, resp.value)
        return resp.value

    def _get_pid_file_name(self, pid):
        print(f"ABS PATH OF CURRENT DIR {os.path.abspath('.')}")
        return "{}/{}".format(self.config["PID_CACHE_DIR"], pid)

    def _pid_file_exists(self, pid):
        print(f"ABS PATH OF CURRENT DIR {os.path.abspath('.')}")
        return os.path.exists(self._get_pid_file_name(pid))

    def _write_pid_file_json(self, pid: str, json_data: dict):
        f = open(self._get_pid_file_name(pid), "w+")
        f.write(json.dumps(json_data))
        f.close()

    def _read_pid_file(self, pid):
        f = open(self._get_pid_file_name(pid), "r")
        txt = ""
        for line in f.readlines():
            txt += line
        f.close()
        return txt
