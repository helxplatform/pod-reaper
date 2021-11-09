import os
from datetime import datetime, timezone
import all_rules.rule as rule

import logger

logger = logger.get_logger(__name__)


class DurationRule(rule.Rule):
    max_pod_duration: int
    rule_name: str

    def load(self):

        if "MAX_POD_DURATION" in os.environ:
            self.max_pod_duration = int(os.getenv("MAX_POD_DURATION"))
        else:
            self.max_pod_duration = 60
            logger.info(f"DURATION rule requires MAX_POD_DURATION (in minutes) to be set. Using default of 60 minutes")

        self.rule_name = "MAX POD DURATION rule"

    def should_reap(self, deployment):

        launch_date_time = deployment.metadata.creation_timestamp
        current_date_time = datetime.now(timezone.utc)
        elapsed_time = current_date_time - launch_date_time
        minutes, seconds = divmod(elapsed_time.total_seconds(), 60)

        if (minutes * 60 + seconds) >= (self.max_pod_duration * 60):
            return True
        else:
            return False
