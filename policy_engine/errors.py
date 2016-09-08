class MethodNotFound(Exception):

    def __init__(self, message):
        super(MethodNotFound, self).__init__(message)


class ConditionParseError(Exception):

    def __init__(self, message):
        super(ConditionParseError, self).__init__(message)


class InvalidPolicy(Exception):

    def __init__(self, message):
        super(InvalidPolicy, self).__init__(message)


class BadCondition(Exception):

    def __init__(self, message):
        super(BadCondition, self).__init__(message)


class MissingParameter(Exception):

    def __init__(self, message):
        super(MissingParameter, self).__init__(message)


class FilterNotFound(Exception):

    def __init__(self, message):
        super(FilterNotFound, self).__init__(message)
