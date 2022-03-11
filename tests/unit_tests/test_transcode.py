import pytest
from mockito import when, unstub, verify, ARGS
from transcode import Transcoder
import base_util

DUMMY_ASSET_ID = "test_asset"
DUMMY_INPUT_DIR = "/dummy/path"
DUMMY_AV_FILE = f"{DUMMY_INPUT_DIR}/{DUMMY_ASSET_ID}.mp4"
DUMMY_AUDIO_FILE = f"{DUMMY_INPUT_DIR}/{DUMMY_ASSET_ID}.mp3"


@pytest.mark.parametrize(
    "input_av_file, output_audio_file, cmd_success", [
        (DUMMY_AV_FILE, DUMMY_AUDIO_FILE, True),
        (DUMMY_AV_FILE, DUMMY_AUDIO_FILE, False),
    ],
)
def test_transcode_to_mp3(application_settings, input_av_file, output_audio_file, cmd_success):
    try:
        transcoder = Transcoder(application_settings)
        when(base_util).run_shell_command(*ARGS).thenReturn(cmd_success)
        success = transcoder.transcode_to_mp3(input_av_file, output_audio_file)
        assert success is cmd_success
        verify(base_util, times=1).run_shell_command(*ARGS)
    finally:
        unstub()


@pytest.mark.parametrize(
    "input_file_path, asset_id", [
        (DUMMY_INPUT_DIR, DUMMY_ASSET_ID),
        (DUMMY_INPUT_DIR.encode("utf-8"), DUMMY_ASSET_ID.encode("utf-8")),  # byte-objects should also  work
        (DUMMY_INPUT_DIR.encode("utf-8"), DUMMY_ASSET_ID),  # mixing strings and bytes also works
    ],
)
def test_get_transcode_output_path(application_settings, input_file_path, asset_id):
    try:
        transcoder = Transcoder(application_settings)
        output_audio_file = transcoder.get_transcode_output_path(input_file_path, asset_id)
        assert output_audio_file is not None
        assert output_audio_file.find(".mp3") != -1
    finally:
        unstub()
