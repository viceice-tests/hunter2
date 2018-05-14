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


class RuntimeValidationError(Exception):
    def __init__(self, message="Runtime validation error"):
        self.message = message
