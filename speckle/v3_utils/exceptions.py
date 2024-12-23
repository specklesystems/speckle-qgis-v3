from specklepy.logging.exceptions import SpeckleException


class UnitNotFoundException(SpeckleException):
    def __init__(self, message: str, exception: SpeckleException = None) -> None:
        super().__init__(message=message, exception=exception)

    def __str__(self) -> str:
        return f"Unsupported unit system: {self.message}"
