"""Custom exceptions for the Terminator SDK."""

class ApiError(Exception):
    """Base exception for API-related errors."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    def __str__(self) -> str:
        if self.status_code:
            return f"API Error ({self.status_code}): {self.message}"
        return f"API Error: {self.message}"

class ConnectionError(ApiError):
    """Raised when connection to the server fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=None)

    def __str__(self) -> str:
        return f"Connection Error: {self.message}" 