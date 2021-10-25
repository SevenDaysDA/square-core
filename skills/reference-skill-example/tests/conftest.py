import pytest
import json
from copy import deepcopy

from starlette.config import environ
MODEL_API_KEY = "test_key"
MODEL_API_URL = "http://localhost:8080/api/<model_name>/<endpoint>"
DATA_API_URL = "http://localhost:8080/datastore/<datastore_name>/indexs/<index_name>/search"
environ["MODEL_API_KEY"] = MODEL_API_KEY
environ["MODEL_API_URL"] = MODEL_API_URL
environ["DATA_API_URL"] = DATA_API_URL

from main import app

data_api_response_json = json.load(open("tests/data_api_response.json"))
model_api_question_answering_response_json = json.load(open("tests/model_api_question_answering_response.json"))


@pytest.fixture()
def test_app():
    return app


@pytest.fixture()
def data_api_response():
    return deepcopy(data_api_response_json)


@pytest.fixture()
def model_api_question_answering_response():
    return deepcopy(model_api_question_answering_response_json)
