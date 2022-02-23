import logging
import os
import subprocess
import yaml
from pathlib import Path

def load_config(cfg_file, app_cfg):
    try:
        with open(cfg_file, 'r') as yamlfile:
            config = yaml.load(yamlfile, Loader=yaml.FullLoader)
            if config:
                app_cfg.update(config)
    except FileNotFoundError as e:
        print(e)
    return app_cfg

def validate_config(cfg, logger):
    valid_log_levels = ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if not cfg['LOG_LEVEL_CONSOLE']  in valid_log_levels or \
        not cfg['LOG_LEVEL_FILE'] in valid_log_levels:
        logger.error('Invalid log level specified in config')
        return False
    return True

def init_cache_dir(cfg, logger):
    logger.info('Checking if the PID cache dir {0} exists'.format(os.path.realpath(cfg['PID_CACHE_DIR'])))
    if not os.path.exists(os.path.realpath(cfg['PID_CACHE_DIR'])):
        logger.info('Path does not exist, creating new dir')
        os.mkdir(os.path.realpath(cfg['PID_CACHE_DIR']))
    else:
        logger.info('PID cache dir already exists')

def validate_data_dirs(cfg, logger):
    i_dir = Path(os.path.join(cfg['BASE_FS_MOUNT_DIR'], cfg['ASR_INPUT_DIR']))
    o_dir = Path(os.path.join(cfg['BASE_FS_MOUNT_DIR'], cfg['ASR_OUTPUT_DIR']))

    if not os.path.exists(i_dir.parent.absolute()):
        logger.debug('{} does not exist. Make sure BASE_FS_MOUNT_DIR exists before retrying'.format(
            i_dir.parent.absolute())
        )
        return False

    #make sure the input and output dirs are there
    try:
        os.makedirs(i_dir, 0o755)
        logger.debug('created ASR input dir: {}'.format(i_dir))
    except FileExistsError as e:
        logger.debug(e)

    try:
        os.makedirs(o_dir, 0o755)
        logger.debug('created ASR output dir: {}'.format(o_dir))
    except FileExistsError as e:
        logger.debug(e)

    return True

def check_language_models(cfg, logger):
    logger.debug("Checking availability of language models; will download if absent")
    fetch_cmd = os.path.join(cfg['KALDI_NL_DIR'], cfg['KALDI_NL_MODEL_FETCHER'])
    logger.debug(fetch_cmd)
    process = subprocess.Popen(fetch_cmd, stdout=subprocess.PIPE, shell=True)
    stdout = process.communicate()[0] # wait until finished. Remove stdout stuff if letting run in background and continue.
    if stdout == '0':
        self.logger.info("models were already downloaded")

def init_logger(log_dir, log_name, log_level_console, log_level_file):
    logger = logging.getLogger(log_name)
    level_file = logging.getLevelName(log_level_file)
    level_console = logging.getLevelName(log_level_console)
    logger.setLevel(level_file)

    # create file handler which logs even debug messages
    if not os.path.exists(os.path.realpath(log_dir)):
        os.mkdir(os.path.realpath(log_dir))

    fh = logging.FileHandler(os.path.join(
        os.path.realpath(log_dir),
        log_name
    ))
    fh.setLevel(level_file)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(level_console)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(process)d|%(module)s|%(funcName)s|%(lineno)d|%(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info("Loaded logger")

    return logger