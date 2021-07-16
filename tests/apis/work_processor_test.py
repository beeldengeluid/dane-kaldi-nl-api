import pytest
from mockito import when, ARGS, KWARGS, unstub, verify
from datetime import datetime

from work_processor import WorkProcessor

DUMMY_PID = '12345'
DUMMY_FILE_PATH = './mount/input-files/test.mp3'

"""
@pytest.mark.parametrize('bad_params', [
    ({'time': '5m', 'size': 1000, 'fromScratch' : True}),
    ({'time': '5m', 'size': 1000, 'update' : False}),
])
"""
def test_simulate_200(application_settings):
    try:
        wp = WorkProcessor(application_settings)

        #mock the call to Elasticsearch
        #when(ElasticSearchHandler).search(i_search, 'dummy-collection').thenReturn(o_search)

        resp = wp.run_simulation(
            DUMMY_PID,
            DUMMY_FILE_PATH,
            False # async
        )
        print(resp)
        assert 'state' in resp and 'message' in resp
        assert resp['state'] == 200
        #assert 'error' not in resp
        #verify(ElasticSearchHandler, times=1).search(i_search, DUMMY_COLLECTION)
    finally:
        unstub()