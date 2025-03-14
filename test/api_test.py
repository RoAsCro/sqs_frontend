import boto3
import pytest
from moto import mock_aws

import apiapp
api = apiapp.api
app = apiapp.app

error_in = api.error_in

good_title = "Title"
good_description = "A description"
good_priority = "high"

bad_title = ""
bad_priority = "not a priority level"

api_path = "/api"

@mock_aws
@pytest.fixture()
def application():
    app.permitted_origins = []
    application = app.create_app()
    api.suggest = lambda message : "No fix suggested."
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


@mock_aws
def test_request_good_request_high(client):
    mock_sqs = boto3.client("sqs", region_name=api.default_region)
    queue = mock_sqs.create_queue(QueueName = "high")['QueueUrl']
    api.sqs = mock_sqs
    api.high_priority = queue
    response = client.post(api_path, json=get_json_dict(
        priority="high",
        title=good_title,
        description=good_description))
    assert response.status_code == 200

@mock_aws
def test_request_good_request_medium(client):
    mock_sqs = boto3.client("sqs", region_name=api.default_region)
    queue = mock_sqs.create_queue(QueueName="high")['QueueUrl']
    api.sqs = mock_sqs
    api.mid_priority = queue
    response = client.post(api_path, json=get_json_dict(
        priority="medium",
        title=good_title,
        description=good_description))
    assert response.status_code == 200

@mock_aws
def test_request_good_request_low(client):
    mock_sqs = boto3.client("sqs", region_name=api.default_region)
    queue = mock_sqs.create_queue(QueueName="high")['QueueUrl']
    api.sqs = mock_sqs
    api.low_priority = queue
    response = client.post(api_path, json=get_json_dict(
        priority="low",
        title=good_title,
        description=good_description))
    assert response.status_code == 200

def test_request_bad_priority(client):
    response = client.post(api_path, json=get_json_dict(
        priority=bad_priority,
        title=good_title,
        description=good_description))
    expected_1 = f"{error_in} priority"
    expected_2 = f"{bad_priority}"
    assert ((bytes(expected_1, 'utf8') and bytes(expected_2, 'utf8')) in response.data
            and response.status_code == 400)

def test_request_bad_title(client):
    response = client.post(api_path, json=get_json_dict(
        priority=good_priority,
        title=bad_title,
        description=good_description))
    expected_1 = f"{error_in} title"
    expected_2 = f"{bad_title}"
    assert ((bytes(expected_1, 'utf8') and bytes(expected_2, 'utf8')) in response.data
            and response.status_code == 400)

def test_request_bad_title_and_priority(client):
    response = client.post(api_path, json=get_json_dict(
        priority=bad_priority,
        title=bad_title,
        description=good_description))
    expected_1 = f"{error_in} title"
    expected_2 = f"{bad_title}"
    expected_3 = f"{error_in} priority"
    expected_4 = f"{bad_priority}"
    assert (((bytes(expected_1, 'utf8') and bytes(expected_2, 'utf8')
            and bytes(expected_3, 'utf8') and bytes(expected_4, 'utf8'))
            in response.data)
            and response.status_code == 400)

def get_json_dict(**kwargs):
    dictionary = {}
    for key, value in kwargs.items():
        dictionary.update({key: value})
    return dictionary
