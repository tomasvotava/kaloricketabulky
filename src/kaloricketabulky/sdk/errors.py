"""Exception hierarchy for the SDK."""


class KaloricError(Exception):
    """Base error for all SDK failures."""


class ApiError(KaloricError):
    """The API envelope returned a non-zero status code."""

    def __init__(self, code: int, message: str | None) -> None:
        self.code = code
        self.api_message = message
        super().__init__(f"API error {code}: {message}")


class AuthError(KaloricError):
    """Authentication failed or no token was available."""
