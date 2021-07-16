import pytest

@pytest.fixture(scope="module")
def o_asr_200(load_json_file):
	return load_json_file(__file__, 'o_asr_200.json')
