# vim: set fileencoding=utf-8 :
from abc import ABCMeta, abstractmethod


class RuntimeExecutionError(Exception):
    def __init__(self, message):
        self.message = message


class RuntimeMemoryExceededError(Exception):
    def __init__(self, message="Runtime memory limit exceeded"):
        self.message = message


class RuntimeExecutionTimeExceededError(Exception):
    def __init__(self, message="Runtime time limit exceeded"):
        self.message = message

class RuntimeSandboxViolationError(Exception):
    def __init__(self, message="Runtime sandbox violation"):
        self.message = message

class AbstractRuntime(metaclass=ABCMeta):
    @abstractmethod
    def evaluate(self, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        """ABSTRACT"""

    @abstractmethod
    # TODO: Consider changing to allow returning a result and unlock hints for this puzzle.
    def validate_guess(self, validator, guess, team_puzzle_data, team_data):
        """ABSTRACT"""
