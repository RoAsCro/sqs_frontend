import json

import pytest
import moto
from moto import mock_aws
from api import error_in

import api
import app

good_title = "Title"
good_description = "A description"

bad_title = ""
bad_priority = "not a priority level"



@pytest.fixture()
def application():
    application = app.create_app()
    application.config.update({
        "TESTING": True,
    })
    yield application

@pytest.fixture()
def client(application):
    return application.test_client()

@pytest.fixture()
def runner(application):
    return application.test_cli_runner()

def test_request_bad_priority(client):
    response = client.post("/api/", json=get_json_dict(
        priority=bad_priority,
        title=good_title,
        description=good_description))
    print(response)
    expected_1 = f"{error_in} priority"
    expected_2 = f"{bad_priority}"
    assert bytes(expected_1, 'utf8') in response.data and bytes(expected_2, 'utf8')

# @mock_aws
# def test_model():
#     api.post_message()

def get_json_dict(**kwargs):
    dictionary = {}
    for key, value in kwargs.items():
        dictionary.update({key: value})
    return dictionary