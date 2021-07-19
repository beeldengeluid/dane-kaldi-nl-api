import pytest
from mockito import when, ARGS, KWARGS, unstub, verify
from datetime import datetime
import time
from apis.APIResponse import APIResponse
from work_processor import WorkProcessor

TEST_MOUNT_DIR = './mount'
TEST_ASR_INPUT_DIR = 'input-files'
TEST_ASR_OUTPUT_DIR = 'asr-output'

DUMMY_PID = '12345'
DUMMY_ASSET_ID = 'test'
DUMMY_FILE_PATH = '{}/{}/{}.mp3'.format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR, DUMMY_ASSET_ID)

""" ------------------- WorkProcessor.run_simulation ------------------- """

def test_run_simulation_200(application_settings):
    try:
        wp = WorkProcessor(application_settings)
        when(time).sleep(5).thenReturn() # mock the sleep call

        resp = wp.run_simulation(
            DUMMY_PID,
            DUMMY_FILE_PATH,
            False # async
        )
        print(resp)
        assert 'state' in resp and 'message' in resp
        assert resp['state'] == 200
        verify(time, times=1).sleep(5)
    finally:
        unstub()

@pytest.mark.parametrize('nonexistent_file', [
    ('FAKE.mp3'),
    ('{}/{}/FAKE.mp3'.format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR)),
])
def test_run_simulation_404(application_settings, nonexistent_file):
    try:
        wp = WorkProcessor(application_settings)
        when(time).sleep(5).thenReturn()

        resp = wp.run_simulation(
            DUMMY_PID,
            nonexistent_file,
            False # async
        )
        print(resp)
        assert 'state' in resp and 'message' in resp
        assert resp['state'] == 404
        verify(time, times=0).sleep(5)
    finally:
        unstub()

""" ------------------- WorkProcessor.process_input_file ------------------- """

def test_process_input_file_200(application_settings):
    try:
        wp = WorkProcessor(application_settings)
        when(wp.asr).run_asr(DUMMY_FILE_PATH, DUMMY_ASSET_ID).thenReturn(None) # mock the run_asr call
        when(wp.asr).process_asr_output(DUMMY_ASSET_ID).thenReturn(APIResponse.ASR_SUCCESS)

        resp = wp.process_input_file(
            DUMMY_PID,
            DUMMY_FILE_PATH,
            False # async
        )
        print(resp)
        assert 'state' in resp and 'message' in resp and 'finished' in resp
        assert resp['state'] == 200
        verify(wp.asr, times=1).run_asr(DUMMY_FILE_PATH, DUMMY_ASSET_ID)
        verify(wp.asr, times=1).process_asr_output(DUMMY_ASSET_ID)
    finally:
        unstub()

@pytest.mark.parametrize('nonexistent_file', [
    ('FAKE.mp3'),
    ('{}/{}/FAKE.mp3'.format(TEST_MOUNT_DIR, TEST_ASR_INPUT_DIR)),
])
def test_process_input_file_404(application_settings, nonexistent_file):
    try:
        wp = WorkProcessor(application_settings)
        when(wp.asr).run_asr(DUMMY_FILE_PATH, DUMMY_ASSET_ID).thenReturn(None) # mock the run_asr call
        when(wp.asr).process_asr_output(DUMMY_ASSET_ID).thenReturn(APIResponse.ASR_FAILED)

        resp = wp.process_input_file(
            DUMMY_PID,
            nonexistent_file,
            False # async
        )
        print(resp)
        assert 'state' in resp and 'message' in resp
        assert resp['state'] == 404
        verify(wp.asr, times=0).run_asr(DUMMY_FILE_PATH, DUMMY_ASSET_ID)
        verify(wp.asr, times=0).process_asr_output(DUMMY_ASSET_ID)
    finally:
        unstub()