class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
