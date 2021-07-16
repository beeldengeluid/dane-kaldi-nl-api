import threading
import os
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
import logging
from work_processor import WorkProcessor
from urllib.parse import quote

api = Namespace('ASR Processing API', description='Process mp3 & wav into text')

_anyField = api.model('AnyField', {})

#See src/tests/unit_tests/apis/basic_search/output_search.json
processResponse = api.model('ProcessResponse', {
	'status' : fields.String(description='whether the ', example="success"),
})

@api.route('/process/<string:pid>',	endpoint='process')
@api.doc(params={
	'input_file': {
		'in': 'query',
		'description': 'path to input file starting from the mounted folder "/input-files"',
		'default': ''
	},
	'pid': {
		'in': 'path',
		'description': 'process code you want to use to track progress (e.g. hash of input_file)',
		'default': ''
	},
	'wait_for_completion' : {
		'in' : 'query',
		'description' : 'wait for the completion of the ASR or not',
		'default' : '1'
	},
	'simulate' : {
		'in' : 'query',
		'description' : 'for development without working ASR available: simulate the ASR',
		'default' : '1'
	}
})
class ProcessEndpoint(Resource):

	#@api.response(200, 'Success', processResponse)
	def put(self, pid):
		input_file = request.args.get('input_file', None)
		wait = request.args.get('wait_for_completion', '1') == '1'
		simulate = request.args.get('simulate', '1') == '1'
		if input_file:
			if wait:
				resp = self._process(pid, input_file, simulate)
			else:
				resp = self._process_async(pid, input_file, simulate)
			return resp, resp['state'], {}
		else:
			return {'state' : 400, 'message' : 'error: bad params'}, 400, {}
		return {'state' : 500, 'message' : 'error: internal server error'}, 500, {}

	#fetch the status of the pid
	def get(self, pid):
		wp = WorkProcessor(current_app.config)
		resp = wp.poll_pid_status(pid)
		return resp, resp['state'], {}

		#process in a different thread, so the client immediately gets a response and can start polling progress via GET
	def _process_async(self, pid, input_file, simulate=True):
		print('starting ASR in different thread...')
		t = threading.Thread(target=self._process, args=(
			pid,
			input_file,
			simulate,
			True,
		))
		t.daemon = True
		t.start()

		#return this response, so the client knows it can start polling
		return {
			'state' : 200,
			'message' : 'submitted the ASR work; status can be retrieved via PID={}'.format(pid),
			'pid' : pid
		}

	def _process(self, pid, input_file, simulate=True, asynchronous=False):
		print('running asr (input_file={}) for PID={}'.format(input_file, pid))
		wp = WorkProcessor(current_app.config)
		if simulate:
			resp = wp.run_simulation(pid, self._to_actual_input_filename(input_file), asynchronous)
		else:
			resp = wp.process_input_file(pid, self._to_actual_input_filename(input_file), asynchronous)
		return resp

	def _to_actual_input_filename(self, input_file):
		return os.path.join(
			current_app.config['BASE_FS_MOUNT_DIR'],
			current_app.config['ASR_INPUT_DIR'],
			quote(input_file)
		)
