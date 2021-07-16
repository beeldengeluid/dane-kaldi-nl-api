import pytest
from mockito import when, ARGS, KWARGS, unstub, verify
from datetime import datetime

from util.APIUtil import APIUtil
from apis.ElasticSearchHandler import ElasticSearchHandler
from apis.basic_search.BasicSearchHandler import BasicSearchHandler
from model.resource_model import Resource

DUMMY_COLLECTION = 'dummy-collection'
DUMMY_OPEN_COLLECTION = 'dummy-open-collection'
ANONYMOUS_TOKEN = 'ANONYMOUS'
DUMMY_RESOURCE_ID = 'dummy-resource-id'
DUMMY_RESOURCE = Resource(DUMMY_RESOURCE_ID, DUMMY_COLLECTION)

def test_search_200(application_settings, application_client, i_search, o_search):
    try:
        bsHandler = BasicSearchHandler(application_settings)

        #mock the call to Elasticsearch
        when(ElasticSearchHandler).search(i_search, 'dummy-collection').thenReturn(o_search)

        resp, status_code, headers = bsHandler.search(
            application_client['id'],
            application_client['token'],
            i_search,
            DUMMY_COLLECTION #TODO dynamically load this?
        )

        assert status_code == 200
        assert 'error' not in resp
        assert all(x in ['hits', 'service', 'timestamp', 'query'] for x in resp)
        assert all(type(resp[x]) == dict for x in ['hits', 'service', 'query'])
        assert type(datetime.strptime(resp['timestamp'], '%Y-%m-%dT%H:%M:%SZ')) == datetime
        assert 'hits' in resp['hits']
        assert type(resp['hits']['hits']) == list
        verify(ElasticSearchHandler, times=1).search(i_search, DUMMY_COLLECTION)
    finally:
        unstub()

def test_search_400(application_settings, application_client):
    try:
        bsHandler = BasicSearchHandler(application_settings)

        #mock the call to Elasticsearch to raise an exception
        when(ElasticSearchHandler).search(*ARGS).thenRaise(
            ValueError('bad_request')
        )

        #just to demonstrate a malformed query (not needed for test)
        malformedQuery = {
            "query": {
                "FAKE": {}
            }
        }

        resp, status_code, headers = bsHandler.search(
            application_client['id'],
            application_client['token'],
            malformedQuery,
            DUMMY_COLLECTION #TODO dynamically load this?
        )

        assert status_code == 400
        assert 'error' in resp
        assert resp['error'] == APIUtil.toErrorMessage('bad_request')
        verify(ElasticSearchHandler, times=1).search(*ARGS)
    finally:
        unstub()

def test_search_403(application_settings, invalid_application_client, i_search, o_search):
    try:
        bsHandler = BasicSearchHandler(application_settings)

        #mock the call to Elasticsearch
        when(ElasticSearchHandler).search(i_search, DUMMY_COLLECTION, None).thenReturn(o_search)

        resp, status_code, headers = bsHandler.search(
            invalid_application_client['id'],
            invalid_application_client['token'],
            i_search,
            DUMMY_COLLECTION #TODO dynamically load this?
        )

        assert status_code == 403
        assert 'error' in resp
        assert resp['error'] == APIUtil.toErrorMessage('access_denied')
        verify(ElasticSearchHandler, times=0).search(*ARGS)
    finally:
        unstub()

def test_search_500(application_settings, application_client, i_search):
    try:
        bsHandler = BasicSearchHandler(application_settings)

        #mock the call to Elasticsearch to raise an exception
        when(ElasticSearchHandler).search(*ARGS).thenRaise(
            ValueError('internal_server_error')
        )

        resp, status_code, headers = bsHandler.search(
            application_client['id'],
            application_client['token'],
            i_search,
            DUMMY_COLLECTION #TODO dynamically load this?
        )

        assert status_code == 500
        assert 'error' in resp
        assert resp['error'] == APIUtil.toErrorMessage('internal_server_error')
        verify(ElasticSearchHandler, times=1).search(*ARGS)
    finally:
        unstub()

def test_search_anonymous_200(application_settings, application_client, i_search, o_search):
    try:
        bsHandler = BasicSearchHandler(application_settings)

        #mock the call to Elasticsearch
        when(ElasticSearchHandler).search(i_search, DUMMY_OPEN_COLLECTION).thenReturn(o_search)

        resp, status_code, headers = bsHandler.search(
            application_client['id'],
            ANONYMOUS_TOKEN, #this is always sent (by a client) for anonymous users
            i_search,
            DUMMY_OPEN_COLLECTION #anonymous user has access to the dummy open collection
        )

        assert status_code == 200
        assert 'error' not in resp
        verify(ElasticSearchHandler, times=1).search(i_search, DUMMY_OPEN_COLLECTION)
    finally:
        unstub()

def test_search_anonymous_403(application_settings, application_client, i_search, o_search):
    try:
        bsHandler = BasicSearchHandler(application_settings)

        #mock the call to Elasticsearch
        when(ElasticSearchHandler).search(i_search, DUMMY_COLLECTION, None).thenReturn(o_search)

        resp, status_code, headers = bsHandler.search(
            application_client['id'],
            ANONYMOUS_TOKEN, #this is always sent (by a client) for anonymous users
            i_search,
            DUMMY_COLLECTION #anonymous user does not have access to the dummy collection
        )

        assert status_code == 403
        assert 'error' in resp
        assert resp['error'] == APIUtil.toErrorMessage('access_denied')
        verify(ElasticSearchHandler, times=0).search(*ARGS)
    finally:
        unstub()

def test_scroll_200(application_settings, application_client, i_scroll, o_scroll):
    try:
        bsHandler = BasicSearchHandler(application_settings)
        when(ElasticSearchHandler).scroll(*ARGS, **KWARGS).thenReturn(o_scroll)

        resp, status_code, headers = bsHandler.scroll(
            application_client['id'],
            application_client['token'],
            DUMMY_COLLECTION,
            params=i_scroll
        )

        assert status_code == 200
        assert 'error' not in resp
        assert all(x in ['results', 'totalHits', '_scroll_id'] for x in resp)
        assert type(resp['results']) == list
        for resource in resp['results']:
            assert all([x in resource for x in DUMMY_RESOURCE.to_json().keys()])
        verify(ElasticSearchHandler, times=1).scroll(*ARGS, **KWARGS)
    finally:
        unstub()

@pytest.mark.parametrize('bad_params', [
    ({'time': '5m', 'size': 1000, 'fromScratch' : True}),
    ({'time': '5m', 'size': 1000, 'update' : False}),
    ({'time': '5m', 'fromScratch' : True, 'update' : False}),
    ({'size': 1000, 'fromScratch' : True, 'update' : False}),
    ({'time': 10, 'size': 1000, 'fromScratch' : True, 'update' : False}),
    ({'time': '5m', 'size': '1000', 'fromScratch' : True, 'update' : False}),
    ({'time': '5m', 'size': 1000, 'fromScratch' : 'true', 'update' : False}),
    ({'time': '5m', 'size': 1000, 'fromScratch' : True, 'update' : 'false'})
])
def test_scroll_400(application_settings, application_client, o_scroll, bad_params):
    try:
        bsHandler = BasicSearchHandler(application_settings)
        when(ElasticSearchHandler).scroll(*ARGS, **KWARGS).thenReturn(o_scroll)

        resp, status_code, headers = bsHandler.scroll(
            application_client['id'],
            application_client['token'],
            DUMMY_COLLECTION,
            params=bad_params
        )

        assert status_code == 400
        assert 'error' in resp
        assert resp['error'] == APIUtil.toErrorMessage('bad_request')
        verify(ElasticSearchHandler, times=0).scroll(*ARGS, **KWARGS)
    finally:
        unstub()


def test_scroll_500(application_settings, application_client, i_scroll):
    try:
        bsHandler = BasicSearchHandler(application_settings)
        when(ElasticSearchHandler).scroll(*ARGS, **KWARGS).thenRaise(ValueError('internal_server_error'))

        resp, status_code, headers = bsHandler.scroll(
            application_client['id'],
            application_client['token'],
            DUMMY_COLLECTION,
            params=i_scroll
        )

        assert status_code == 500
        assert 'error' in resp
        assert resp['error'] == APIUtil.toErrorMessage('internal_server_error')
        verify(ElasticSearchHandler, times=1).scroll(*ARGS, **KWARGS)
    finally:
        unstub()

# make sure to install the chrome driver for this to work: https://sites.google.com/a/chromium.org/chromedriver/home
# FIXME this will not work yet on the server!
# FIXME make sure the chrome drive can be mocked!
"""
def test_scroll_update(application_settings, application_client, i_scroll, o_scroll):
    try:
        params = i_scroll
        params['update'] = True
        bsHandler = BasicSearchHandler(application_settings)
        when(ElasticSearchHandler).scroll(*ARGS, **KWARGS).thenReturn(o_scroll)

        resp, status_code, headers = bsHandler.scroll(
            application_client['id'],
            application_client['token'],
            DUMMY_COLLECTION,
            params=params
        )

        assert status_code == 200
        assert 'error' not in resp
        assert all(x in ['results', 'totalHits', '_scroll_id'] for x in resp)
        assert type(resp['results']) == list
        verify(ElasticSearchHandler, times=1).scroll(*ARGS, **KWARGS)
    finally:
        unstub()
"""
