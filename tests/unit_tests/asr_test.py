import pytest
from mockito import when, unstub, verify, ARGS
from asr import ASR
import base_util


DUMMY_ASSET_ID = "test_asset"
DUMMY_INPUT_DIR = "/dummy/path"
DUMMY_AV_FILE = f"{DUMMY_INPUT_DIR}/{DUMMY_ASSET_ID}.mp4"
DUMMY_AUDIO_FILE = f"{DUMMY_INPUT_DIR}/{DUMMY_ASSET_ID}.mp3"


@pytest.mark.parametrize(
    "input_path, asset_id, cmd_success", [
        (DUMMY_INPUT_DIR, DUMMY_ASSET_ID, True),
        (DUMMY_INPUT_DIR, DUMMY_ASSET_ID, False),
    ],
)
def test_run_asr(application_settings, input_path, asset_id, cmd_success):
    try:
        asr = ASR(application_settings)
        when(base_util).run_shell_command(*ARGS).thenReturn(cmd_success)
        success = asr.run_asr(input_path, asset_id)
        assert success is cmd_success
        verify(base_util, times=1).run_shell_command(*ARGS)
    finally:
        unstub()


def test_process_asr_output(application_settings):
    try:
        asr = ASR(application_settings)
        # TODO
    finally:
        unstub()


def test_validate_asr_output(application_settings):
    try:
        asr = ASR(application_settings)
        # TODO
    finally:
        unstub()


def test_package_output(application_settings):
    try:
        asr = ASR(application_settings)
        # TODO
    finally:
        unstub()


def test_create_word_json(application_settings):
    try:
        asr = ASR(application_settings)
        # TODO
    finally:
        unstub()


def test_get_output_dir(application_settings):
    try:
        asr = ASR(application_settings)
        # TODO
    finally:
        unstub()


def test_get_transcript_file_path(application_settings):
    try:
        asr = ASR(application_settings)
        # TODO
    finally:
        unstub()


def test_get_words_file_path(application_settings):
    try:
        asr = ASR(application_settings)
        # TODO
    finally:
        unstub()
