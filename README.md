# ASR API

This API is currently built on top of Kaldi_NL and supports both synchronous and asynchronous REST calls to invoke the processing of audiovisual files for obtaining speech transcripts (generated by ASR)

## Local install

Make sure to create the central config file: `config/settings.py`. You can easily do this by copying the `config/settings-example.py` to `settings.py`


```
DEBUG : bool = True

#debug service settings (settings.py)
APP_HOST : str = '0.0.0.0'
APP_PORT : int = 3023

# relative from the server.py
BASE_FS_MOUNT_DIR : str = './mount' # /mnt/dane-fs when running in docker/k8s

#asr module settings (asr.py)
ASR_INPUT_DIR : str = 'input-files' # will be created in BASE_FS_MOUNT_DIR
ASR_OUTPUT_DIR : str = 'asr-output' # will be created in BASE_FS_MOUNT_DIR
ASR_PACKAGE_NAME : str = 'asr-features.tar.gz'
ASR_WORD_JSON_FILE : str = 'words.json'

#(as module) kaldi NL base dir and the decoder script therein
KALDI_NL_DIR : str = '/usr/local/opt/kaldi_nl' # without a local KaldiNL only simulation mode is possible
KALDI_NL_DECODER : str = 'decode_OH.sh'

PID_CACHE_DIR : str = 'pid-cache' # relative from the server.py dir

LOG_DIR : str = "log" # relative from the server.py dir
LOG_NAME : str = "asr-service.log"
LOG_LEVEL_CONSOLE : str = "DEBUG" # Levels: NOTSET - DEBUG - INFO - WARNING - ERROR - CRITICAL
LOG_LEVEL_FILE : str = "DEBUG" # Levels: NOTSET - DEBUG - INFO - WARNING - ERROR - CRITICAL
```


### Create virtual environment

Create a Python 3 virtual environment:

```
python3 -m venv venv
```

**Note**: the venv dir is added to the `.gitignore`, so it's good to keep this name for your virtual environment

Now activate the virtual environment and install the required Python libraries:

```
. venv/bin/activate
pip install -r requirements.txt
```

### Run the server

When you have activated the virtual environment with all the installed packages, you can run the server with:

```
python server.py
```