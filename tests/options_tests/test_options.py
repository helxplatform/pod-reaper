from pytest import mark
from options import Options


@mark.options
class OptionsTests:

    def test_reaper_options_loading(self, mock_options_env_variables):
        options = Options.load_options()
        assert options.namespace == "test-namespace"
        assert options.grace_period == 30
