import os
import json
import sys
from json import JSONDecodeError

import logger

logger = logger.get_logger(__name__)


def get_namespace(namespace="default"):
    """Using downward API to get the pod namespace. Defaults to 'default' namespace"""

    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as secrets:
            for line in secrets:
                namespace = line
                break

    except FileNotFoundError as e:
        logger.info(f"Downward api namespace lookup failed. Using default namespace.")

    return namespace


def get_run_duration():
    """Default run duration of pod_reaper is 0 - Runs indefinitely"""

    return float(os.getenv("RUN_DURATION", 0))


def get_schedule():
    """Default schedule every 30 seconds"""

    schedule = int(os.getenv("SCHEDULE", 300))

    return schedule


def get_required_keys_values():
    """Get a comma separated list of labels for the corresponding key"""

    try:
        required_keys_values = json.loads(os.getenv("REQUIRED_KEYS_VALUES", None))
        if required_keys_values:
            return required_keys_values
    except (JSONDecodeError, TypeError) as e:
        logger.error(f"Exception at loading required keys and values. {e}."
                     f" Set the environment variable REQUIRED_KEYS_VALUES")
        sys.exit()


class Options:

    def __init__(self, *args):

        self.namespace = args[0]
        self.run_duration = args[1]
        self.schedule = args[2]
        self.required_keys_values = args[3]

    @staticmethod
    def load_options():
        logger.info("Loading preferred Options(labels, max_duration etc.) and Kubernetes APIs")
        namespace = os.getenv("NAMESPACE", get_namespace())
        run_duration = get_run_duration()
        schedule = get_schedule()
        required_keys_values = get_required_keys_values()

        return Options(
            namespace,
            run_duration,
            schedule,
            required_keys_values,
        )
