PY_ERROR_TYPES = [TypeError, KeyError, AttributeError]


class BaseError(Exception):
    def __init__(self, message, status, *args, **kwargs):
        self.message = message
        self.status = status
        super().__init__(self.message, self.status)


class BadRequestError(BaseError):
    def __init__(self, message="", status=400):
        self.message = f"Bad Request: {message}"
        self.status = status
        super().__init__(self.message, self.status)


class ForbiddenError(BaseError):
    def __init__(self, message="", status=403):
        self.message = f"Forbidden: {message}"
        self.status = status
        super().__init__(self.message, self.status)


class NotFoundError(BaseError):
    def __init__(self, message="", status=404):
        self.message = f"Not Found: {message}"
        self.status = status
        super().__init__(self.message, self.status)


class ConflictError(BaseError):
    def __init__(self, message="Conflict", status=409):
        self.message = message
        self.status = status
        super().__init__(self.message, self.status)


class UnprocessedContentError(BaseError):
    def __init__(self, message="Unprocessed Content", status=422):
        self.message = message
        self.status = status
        super().__init__(message, status)


class PreconditionRequiredError(BaseError):
    def __init__(self, message="Precondition Required", status=428):
        self.message = message
        self.status = status
        super().__init__(message, status)
