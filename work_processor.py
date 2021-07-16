import os
import ntpath
import shutil
import logging
import json
from time import sleep
from asr import ASR
from transcode import transcode_to_mp3
from flask import current_app

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
		self.logger = logging.getLogger(config['LOG_NAME'])
		self.asr = ASR(config)

	#simulates running ASR and/or transcoding, so the API communication can be tested in isolation
	def run_simulation(self, pid, input_file_path, asynchronous=False):
		self.logger.debug('simlating ASR, but verifying the validity of the request params')
		self.logger.debug(input_file_path)

		#first write to the PID that the process is busy, then sleep for 5 seconds to simulate ASR/transcoding
		self._write_pid_file_json(pid, {
			'state' : 200, 'message' : 'Simulation in progress'
		})
		if not os.path.isfile(input_file_path):  # check if inputfile exists
			return self._resp_to_pid_file(pid, asynchronous, {
				'state': 404, 'message': 'No file found at file location {0}'.format(input_file_path)
			})
		else:
			sleep(5)
			return self._resp_to_pid_file(pid, asynchronous, {
				'state' : 200, 'message' : 'Succesfully ran ASR on {0}'.format(input_file_path)
			})

	#processes the input and keeps a PID file with status information in asynchronous mode
	def process_input_file(self, pid, input_file_path, asynchronous=False):
		self.logger.debug('processing {} for PID={}'.format(input_file_path, pid))
		if not os.path.isfile(input_file_path):  # check if inputfile exists
			return self._resp_to_pid_file(pid, asynchronous, {
				'state': 404, 'message': 'No file found at file location {0}'.format(input_file_path)
			})

		#grab the file_name from the path
		file_name = ntpath.basename(input_file_path)

		#split up the file in asset_id (used for creating a subfolder in the output) and extension
		asset_id, extension = os.path.splitext(file_name)

		#first assume the file is a valid audio file
		asr_input_path = input_file_path

		#check if the input file is a valid audio file, if not: transcode it first
		if not self._is_audio_file(extension):
			if self._is_transcodable(extension):
				asr_input_path = os.path.join(
					os.sep,
					os.path.dirname(input_file_path), #the dir the input file is in
					asset_id + ".mp3" #same name as input file, but with mp3 extension
				)
				self.transcode_to_mp3(
					input_file_path,
					asr_input_path #the transcode output is the input for the ASR
				)
			else:
				return self._resp_to_pid_file(pid, asynchronous, {
					'state': 406,
					'message': 'Not acceptable: accepted file formats are; mov,mp4,m4a,3gp,3g2,mj2'
				})

		#run the ASR
		try:
			self.asr.run_asr(asr_input_path, asset_id)
		except Exception as e:
			return _resp_to_pid_file(pid, asynchronous, {
				'state': 500,
				'message': 'Something went wrong when encoding the file: {0}'.format(e)
			})

		#finally process the ASR results and return the status message
		return self._resp_to_pid_file(pid, asynchronous, self.asr.process_asr_output(asset_id))

	def poll_pid_status(self, pid):
		self.logger.debug('Getting status for pid {}'.format(pid))
		if not self._pid_file_exists(pid):
			return {'state' : 404, 'message' : 'Error: PID does not exist (anymore)'}

		status = self._read_pid_file(pid)
		try:
			return json.loads(status)
		except Exception as e:
			return {'state' : 500, 'message' : 'PID file was corrupted'}

	def _is_audio_file(self, extension):
		return extension in ['.mp3', '.wav']

	def _is_transcodable(self, extension):
		return extension in [".mov", ".mp4", ".m4a", ".3gp", ".3g2", ".mj2"]

	#clean up input files
	def _remove_files(self, path):
		for file in os.listdir(path):
			file_path = os.path.join(path, file)
			try:
				if os.path.isfile(file_path) or os.path.islink(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except Exception as e:
				print('Failed to delete {0}. Reason: {1}'.format(file_path, e))

	"""-------------------------------------- PID FILE FUNCTIONS -----------------------------------------------"""

	#writes the API response to the PID file, if the "ASR job" is running asynchronously
	def _resp_to_pid_file(self, pid, asynchronous, resp):
		self.logger.debug(resp)
		if asynchronous:
			self._write_pid_file_json(pid, resp)
		return resp

	def _get_pid_file_name(self, pid):
		return '{}/{}'.format(self.config['PID_CACHE_DIR'], pid)

	def _pid_file_exists(self, pid):
		return os.path.exists(self._get_pid_file_name(pid))

	def _write_pid_file_json(self, pid, json_data):
		f  = open(self._get_pid_file_name(pid), 'w+')
		f.write(json.dumps(json_data))
		f.close()

	def _read_pid_file(self, pid):
		f  = open(self._get_pid_file_name(pid), 'r')
		txt = ''
		for l in f.readlines():
			txt += l
		f.close()
		return txt