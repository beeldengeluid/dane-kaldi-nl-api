from flask import Flask
from flask import Response

from apis import api
from base_util import (
    load_config,
    init_logger,
    validate_config,
    validate_data_dirs,
    init_cache_dir,
    check_language_models,
)

app = Flask(__name__)

app.config = load_config("./config/settings.yaml", app.config)

if not app.config:
    quit()

# initiliaze the logger
logger = init_logger(
    app.config["LOG_DIR"],
    app.config["LOG_NAME"],
    app.config["LOG_LEVEL_CONSOLE"],
    app.config["LOG_LEVEL_FILE"],
)

if not validate_config(app.config, logger):
    logger.error("settings.yaml was not valid, quitting...")
    quit()

# now specifically validate the configured data input & output dirs
if not validate_data_dirs(app.config, logger):
    logger.error("configured data dirs not ok, quitting...")
    quit()

# make sure the language models are downloaded
if not check_language_models(app.config, logger):
    logger.error("could not properly download required language models, quitting...")
    quit()

# make sure the cache dir for the PIDs exists
init_cache_dir(app.config, logger)

logger.info("Initializing process API")

# the api catches all the ASR processing requests (see the process_api.py)
api.init_app(
    app,
    title="Beeld en Geluid ASR container",
    description="Access the speech transcription service within this docker container",
)


# heartbeat check called by external "health monitor"
@app.route("/ping")
def ping():
    logger.debug("/ping was called")
    return Response("pong", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host=app.config["APP_HOST"], port=app.config["APP_PORT"])
