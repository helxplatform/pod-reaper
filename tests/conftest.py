import os
import json
import kubernetes
from pathlib import Path

from pytest import mark
from pytest import fixture

from config import Config

conf = Config(os.environ.get("TEST_ENV", "dev"))

# Reaper module fixtures
@fixture
def mock_reaper_env_variables(mocker):
    mocker.patch.dict("os.environ", {"RUN_DURATION": "2",
                                     "GRACE_PERIOD": "1",
                                     "SCHEDULE": "300",
                                     "REQUIRED_KEYS_VALUES": '{"test-name": ["nginx", "nginx-1"],'
                                                             '"test-executor": ["pytest"]}',
                                     "MAX_POD_DURATION": "2",
                                     "NAMESPACE": "muralikarthik-k"})
    yield


# Options module fixtures
@fixture
def mock_options_env_variables(mocker):
    mocker.patch.dict("os.environ", {"NAMESPACE": "test-namespace",
                                     "RUN_DURATION": "0",
                                     "GRACE_PERIOD": "30",
                                     "SCHEDULE": "2000",
                                     "REQUIRED_KEYS_VALUES": '{"test-name": ["nginx", "nginx-1"],'
                                                             '"test-executor": ["pytest"]}'
                                     })
    yield


##################################################################################

# def get_options_data_files(path):
#     files = Path(path).glob("*.json")
#     for file in files:
#         with open(file) as data_file:
#             return json.load(data_file)
#
#
# @fixture(scope="session", params=get_options_data_files(conf.options_data_path))
# def get_options(request):
#     options = request.param
#     return options


# def pytest_addoption(parser):
#     parser.addoption(
#         "--env",
#         action="store",
#         default="dev",
#         help="Environment to run tests against"
#     )


# def pod_reaper_config(env):
#     cfg = Config(env)
#     return cfg

