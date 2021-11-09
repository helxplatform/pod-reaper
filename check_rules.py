import sys

import logger as logger

from all_rules.duration import DurationRule

logger = logger.get_logger(__name__)


class RulesLoader:
    loaded_rules: list

    def load_rules(self):
        """Load all the available rules."""

        default_rules = [
            DurationRule()
        ]

        other_rules = []

        loaded_rules = []

        for rule in default_rules:
            rule.load()
            loaded_rules.append(rule)

        for rule in other_rules:
            if rule.load():
                loaded_rules.append(rule)
            else:
                continue

        self.loaded_rules = loaded_rules

    def should_reap(self, deployment):
        """Sets the reap status of a deployment to True if any one of the rule promotes it for reaping.
            One rule is adequate for a deployment to be reaped."""

        reap_pod = False

        for loaded_rule in self.loaded_rules:
            resp = loaded_rule.should_reap(deployment)
            if resp:
                logger.info(f"Reaping pod based on rule: {loaded_rule.rule_name}")
                return True

        return reap_pod
