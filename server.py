from flask import Flask
from flask import Response

from apis import api
from init_util import load_config, init_logger, validate_config, validate_data_dirs, init_cache_dir

app = Flask(__name__)

app.config = load_config('./config/settings.yaml', app.config)

if not app.config:
    quit()

#initiliaze the logger
logger = init_logger(
    app.config['LOG_DIR'],
    app.config['LOG_NAME'],
    app.config['LOG_LEVEL_CONSOLE'],
    app.config['LOG_LEVEL_FILE']
)

if not validate_config(app.config, logger):
    quit()

# now specifically validate the configured data input & output dirs
if  not validate_data_dirs(app.config, logger):
    quit()

# make sure the cache dir for the PIDs exists
init_cache_dir(app.config, logger)

logger.info('Initializing process API')

# the api catches all the ASR processing requests (see the process_api.py)
api.init_app(
    app,
    title='Beeld en Geluid ASR container',
    description='Access the speech transcription service within this docker container'
)

# heartbeat check called by external "health monitor"
@app.route('/ping')
def ping():
    logger.debug('/ping was called')
    return Response('pong', mimetype='text/plain')

if __name__ == '__main__':
    app.run(host=app.config['APP_HOST'], port=app.config['APP_PORT'])
