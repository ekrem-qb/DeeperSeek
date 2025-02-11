class DeeperSeekException(BaseException):
    pass


class InvalidConversationID(DeeperSeekException):
    pass


class MissingCredentials(DeeperSeekException):
    pass


class InvalidCredentials(DeeperSeekException):
    pass


class ServerDown(DeeperSeekException):
    pass
