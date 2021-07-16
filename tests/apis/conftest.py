import pytest

@pytest.fixture(scope="module")
def i_search(load_json_file):
    return load_json_file(__file__, 'input_search.json')

@pytest.fixture(scope="module")
def o_search(load_json_file):
    return load_json_file(__file__, 'output_search.json')

@pytest.fixture(scope="module")
def i_scroll(load_json_file):
    return load_json_file(__file__, 'input_scroll.json')

@pytest.fixture(scope="module")
def o_scroll(load_json_file):
    return load_json_file(__file__, 'output_scroll.json')
