from flask import Flask
import json
import os
import pytest
from base_util import load_config

"""
Basic fixtures that are useful for most of the test modules
"""

"""------------------------ APPLICATION BASE PATH/URL ----------------------"""


@pytest.fixture(scope="session")
def base_path():
    return "/api"


@pytest.fixture(scope="session")
def base_url(application_settings, base_path):
    return "http://localhost:%s%s" % (application_settings["APP_PORT"], base_path)


@pytest.fixture(scope="session")
def base_file_path():
    parts = os.path.realpath(__file__).split(os.sep)
    return os.sep.join(parts[0 : len(parts) - 2])


@pytest.fixture(scope="module")
def load_json_file():
    def loadJSONFile(test_path, fn):
        path = test_path
        tmp = test_path.split(os.sep)
        if len(tmp) > 1:
            path = os.sep.join(test_path.split(os.sep)[:-1])
        full_path = os.path.join(path, fn)
        if os.path.exists(full_path):
            return json.load(open(full_path))
        return None

    return loadJSONFile


"""------------------------ APPLICATION SETTINGS (VALID) ----------------------"""


@pytest.fixture(scope="module")
def ckan_cache(load_json_file):
    return load_json_file(__file__, "ckan_cache.json")


"""------------------------ APPLICATION SETTINGS (VALID) ----------------------"""


@pytest.fixture(scope="session")
def application_settings():
    app = Flask(__name__)
    app.config = load_config("./config/settings_example.yaml", app.config)
    return app.config


"""------------------------ API CLIENTS FOR ON & OFFLINE TESTING ----------------------"""


@pytest.fixture(scope="session")
def flask_test_client():
    from server import app

    return app.test_client()


@pytest.fixture(scope="session")
def http_test_client(application_settings):
    import requests

    class HTTPClient:
        def post(self, path, data=None):
            return requests.post(
                "http://%s:%s%s"
                % (
                    application_settings["APP_HOST"],
                    application_settings["APP_PORT"],
                    path,
                ),
                json=data,
            )

        def get(self, path):
            return requests.get(
                "http://localhost:%s%s" % (application_settings["APP_PORT"], path)
            )

    return HTTPClient()


@pytest.fixture(scope="session")
def generic_client(http_test_client, flask_test_client):
    class Response(object):
        def __init__(self, text, status_code, headers):
            self.text = text
            self.status_code = status_code
            self.headers = headers

    class GenericClient:
        def post(self, mode, path, data=None):
            if mode == "offline":
                r = flask_test_client.post(
                    path, data=json.dumps(data), content_type="application/json"
                )
                return Response(r.data, r.status_code, r.headers)
            else:
                return http_test_client.post(path, data=data)

        def get(self, mode, path):
            if mode == "offline":
                r = flask_test_client.get(path)
                return Response(r.data, r.status_code, r.headers)
            else:
                return http_test_client.get(path)

    return GenericClient()
