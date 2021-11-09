import os


class Config:
    def __init__(self, env):

        supported_envs = ['dev']
        tests_dir = os.path.dirname(os.path.abspath(__file__))

        if env.lower() not in supported_envs:
            raise Exception(f'{env} is not a supported environment (supported envs: {supported_envs})')

        self.options_data_path = {
            'dev': os.path.join(tests_dir, "options_tests", "data"),
        }[env]

        self.reaper_data_path = {
            'dev': os.path.join(tests_dir, "reaper_tests", "data"),
        }[env]
