from pytest import mark
from reaper import Reaper


@mark.reaper
def test_reaper(mock_reaper_env_variables):
    reaper = Reaper()
    reaper.harvest()
    assert False
