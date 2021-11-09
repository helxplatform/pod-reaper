from abc import ABC, abstractmethod


class Rule(ABC):

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def should_reap(self, deployment):
        pass
