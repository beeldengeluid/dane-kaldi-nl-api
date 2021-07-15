from flask import Flask
from flask import render_template
from flask import request, Response

import os
import json
from config.settings import APP_HOST, APP_PORT, PID_CACHE_DIR, LOG_DIR, LOG_NAME, \
	LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE, DEBUG, \
	BASE_FS_MOUNT_DIR, ASR_INPUT_DIR, ASR_OUTPUT_DIR
from work_processor import process_input_file
from apis import api
from logging_util import init_logger
from pathlib import Path

"""
decided to stick to OAS 2.0 after looking for good tools for supporting OAS 3.0. It
seems it is smart to wait a bit for better support: https://developer.acronis.com/blog/posts/raml-vs-swagger/
Note: you can check support pretty well with https://editor.swagger.io/
"""

app = Flask(__name__)
app.config['DEBUG'] = DEBUG

#initiliaze the logger
logger = init_logger(LOG_DIR, LOG_NAME, LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE)

logger.info('Initializing process API')

api.init_app(
	app,
	title='Beeld en Geluid ASR container',
    description='Access the speech transcription service within this docker container'
)

"""-------------------- INIT FUNCTIONS ------------------"""

def validate_config():
	valid_log_levels = ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
	if not LOG_LEVEL_CONSOLE  in valid_log_levels or not LOG_LEVEL_FILE in valid_log_levels:
		logger.error('Invalid log level specified in config')
		return False
	return True

def init_cache_dir():
	logger.info('Checking if the PID cache dir {0} exists'.format(os.path.realpath(PID_CACHE_DIR)))
	if not os.path.exists(os.path.realpath(PID_CACHE_DIR)):
		logger.info('Path does not exist, creating new dir')
		os.mkdir(os.path.realpath(PID_CACHE_DIR))
	else:
		logger.info('PID cache dir already exists')

def validate_data_dirs():
	i_dir = Path(os.path.join(BASE_FS_MOUNT_DIR, ASR_INPUT_DIR))
	o_dir = Path(os.path.join(BASE_FS_MOUNT_DIR, ASR_OUTPUT_DIR))

	if not os.path.exists(i_dir.parent.absolute()):
		logger.debug('{} does not exist. Make sure BASE_FS_MOUNT_DIR exists before retrying'.format(
			i_dir.parent.absolute())
		)
		return False

	#make sure the input and output dirs are there
	try:
		os.mkdir(i_dir, 0o755)
		logger.debug('created ASR input dir: {}'.format(i_dir))
	except FileExistsError as e:
		logger.debug(e)

	try:
		os.mkdir(o_dir, 0o755)
		logger.debug('created ASR output dir: {}'.format(o_dir))
	except FileExistsError as e:
		logger.debug(e)

	return True

# validate the config
if not validate_config():
	quit()

# now specifically validate the configured data input & output dirs
if  not validate_data_dirs():
	quit()

# make sure the cache dir for the PIDs exists
init_cache_dir()


"""------------------------------------------------------------------------------
PING / HEARTBEAT ENDPOINT
------------------------------------------------------------------------------"""

@app.route('/ping')
def ping():
	logger.debug('/ping was called')
	return Response('pong', mimetype='text/plain')

"""------------------------------------------------------------------------------
REGULAR ROUTING (STATIC CONTENT)
------------------------------------------------------------------------------"""
@app.route('/debug')
def home():
	logger.debug('/debug was called')
	return render_template('index.html')

@app.route('/process-debug', methods=['POST'])
def debug():
	input_file = request.form.get('input_file', None)
	resp = process_input_file(os.path.join(os.sep, 'input-files', input_file))
	return Response(json.dumps(resp), mimetype='application/json')

if __name__ == '__main__':
	app.run(host=APP_HOST, port=APP_PORT)
