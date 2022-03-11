import pytest
from mockito import when, ARGS, unstub, verify
import time
from api_util import APIResponse
from work_processor import WorkProcessor
from uuid import uuid4
from transcode import Transcoder

TEST_MOUNT_DIR = "./tests/unit_tests/mount"
TEST_ASR_INPUT_DIR = "input-files"
TEST_ASR_OUTPUT_DIR = "asr-output"

DUMMY_PID = "unit_test_pid"
DUMMY_ASSET_ID = "test"
DUMMY_FILE_PATH_MP3 = "{}/{}/{}.mp3".format(
    TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR, DUMMY_ASSET_ID
)
DUMMY_FILE_PATH_MP4 = "{}/{}/{}.mp4".format(
    TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR, DUMMY_ASSET_ID
)

""" ------------------- WorkProcessor.run_simulation ------------------- """


def test_run_simulation_200(application_settings):
    try:
        wp = WorkProcessor(application_settings)
        when(time).sleep(5).thenReturn()  # mock the sleep call

        resp = wp.run_simulation(DUMMY_PID, DUMMY_FILE_PATH_MP3, False)  # async
        assert "state" in resp and "message" in resp
        assert resp["state"] == 200
        assert wp._pid_file_exists(
            DUMMY_PID
        )  # make sure test/pid-cache/[DUMMY_PID] exists
        verify(time, times=1).sleep(5)
    finally:
        unstub()


@pytest.mark.parametrize(
    "nonexistent_file",
    [
        ("FAKE.mp3"),
        ("{}/{}/FAKE.mp3".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR)),
    ],
)
def test_run_simulation_404(application_settings, nonexistent_file):
    try:
        wp = WorkProcessor(application_settings)
        when(time).sleep(5).thenReturn()

        resp = wp.run_simulation(DUMMY_PID, nonexistent_file, False)  # async
        assert "state" in resp and "message" in resp
        assert resp["state"] == 404
        verify(time, times=0).sleep(5)
    finally:
        unstub()


""" ------------------- WorkProcessor.process_input_file ------------------- """


def test_process_input_file_200(application_settings):
    try:
        wp = WorkProcessor(application_settings)
        when(wp.asr).run_asr(DUMMY_FILE_PATH_MP3, DUMMY_ASSET_ID).thenReturn(
            None
        )  # mock the run_asr call
        when(wp.asr).process_asr_output(DUMMY_ASSET_ID).thenReturn(
            APIResponse.ASR_SUCCESS
        )

        resp = wp.process_input_file(DUMMY_PID, DUMMY_FILE_PATH_MP3, False)  # async
        print(resp)
        assert "state" in resp and "message" in resp and "finished" in resp
        assert resp["state"] == 200
        verify(wp.asr, times=1).run_asr(DUMMY_FILE_PATH_MP3, DUMMY_ASSET_ID)
        verify(wp.asr, times=1).process_asr_output(DUMMY_ASSET_ID)
    finally:
        unstub()


@pytest.mark.parametrize(
    "nonexistent_file",
    [
        ("FAKE.mp3"),
        ("{}/{}/FAKE.mp3".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR)),
    ],
)
def test_process_input_file_404(application_settings, nonexistent_file):
    try:
        wp = WorkProcessor(application_settings)
        when(wp.asr).run_asr(DUMMY_FILE_PATH_MP3, DUMMY_ASSET_ID).thenReturn(
            None
        )  # mock the run_asr call
        when(wp.asr).process_asr_output(DUMMY_ASSET_ID).thenReturn(
            APIResponse.ASR_FAILED
        )

        resp = wp.process_input_file(DUMMY_PID, nonexistent_file, False)  # async
        print(resp)
        assert "state" in resp and "message" in resp
        assert resp["state"] == 404
        verify(wp.asr, times=0).run_asr(DUMMY_FILE_PATH_MP3, DUMMY_ASSET_ID)
        verify(wp.asr, times=0).process_asr_output(DUMMY_ASSET_ID)
    finally:
        unstub()


""" ------------------- WorkProcessor._try_transcode ------------------- """


def test_try_transcode_200(application_settings):
    try:
        wp = WorkProcessor(application_settings)
        when(wp.transcoder).transcode_to_mp3(*ARGS).thenReturn()
        try:
            resp = wp._try_transcode(DUMMY_FILE_PATH_MP4, "test", ".mp4")
            assert resp == wp.transcoder.get_transcode_output_path(DUMMY_FILE_PATH_MP4, "test")
        except ValueError as e:
            print(e)
        verify(wp.transcoder, times=1).transcode_to_mp3(*ARGS)
    finally:
        unstub()


@pytest.mark.parametrize(
    "asr_input_path, extension",
    [
        ("{}/{}/test.txt".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR), ".txt"),
        ("{}/{}/test.rtf".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR), ".rtf"),
        ("{}/{}/test.dat".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR), ".dat"),
        ("{}/{}/test.sh".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR), ".sh"),
        ("{}/{}/test.bin".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR), ".bin"),
        ("{}/{}/test.avi".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR), ".avi"),
        ("{}/{}/test.flac".format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR), ".flac"),
    ],
)
def test_try_transcode_406(application_settings, asr_input_path, extension):
    try:
        wp = WorkProcessor(application_settings)
        when(wp.transcoder).transcode_to_mp3(*ARGS).thenReturn()
        try:
            wp._try_transcode(asr_input_path, "test", extension)
        except ValueError as e:
            assert APIResponse[str(e)] == APIResponse.ASR_INPUT_UNACCEPTABLE
        verify(wp.transcoder, times=0).transcode_to_mp3(*ARGS)
    finally:
        unstub()


def test_try_transcode_500(application_settings):
    try:
        wp = WorkProcessor(application_settings)
        when(wp.transcoder).transcode_to_mp3(*ARGS).thenReturn(False)
        try:
            wp._try_transcode(DUMMY_FILE_PATH_MP4, "test", ".mp4")
        except ValueError as e:
            assert APIResponse[str(e)] == APIResponse.TRANSCODE_FAILED
        verify(wp.transcoder, times=1).transcode_to_mp3(*ARGS)
    finally:
        unstub()


""" ------------------- WorkProcessor.poll_pid_status ------------------- """


def test_poll_pid_status_200(application_settings):
    try:
        wp = WorkProcessor(application_settings)

        resp = wp.poll_pid_status(DUMMY_PID)
        assert "state" in resp and "message" in resp
        assert wp._pid_file_exists(
            DUMMY_PID
        )  # make sure test/pid-cache/[DUMMY_PID] exists
    finally:
        unstub()


@pytest.mark.parametrize("nonexistent_pid", [(uuid4()) for x in range(0, 5)])
def test_poll_pid_status_404(application_settings, nonexistent_pid):
    try:
        wp = WorkProcessor(application_settings)

        resp = wp.poll_pid_status(nonexistent_pid)
        assert "state" in resp and "message" in resp
        assert resp == APIResponse.PID_NOT_FOUND.value
    finally:
        unstub()


@pytest.mark.parametrize(
    "corrupt_json",
    [
        ('{"state" : 200, "message" : "success}'),  # missing a "
        ("{'state' : 200, 'message' : 'success'"),  # ' instead of "
        ("brush crackle fizzly"),  # just a random string
        (uuid4()),  # just a random number
    ],
)
def test_poll_pid_status_500(application_settings, corrupt_json):
    try:
        wp = WorkProcessor(application_settings)
        when(wp)._read_pid_file(DUMMY_PID).thenReturn(corrupt_json)
        resp = wp.poll_pid_status(DUMMY_PID)
        assert resp == APIResponse.PID_FILE_CORRUPTED.value
    finally:
        unstub()
