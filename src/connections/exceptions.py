class ConnectionsError(Exception):
    """Base class for Connections errors."""


class InvalidGuessError(ConnectionsError):
    """A guess was malformed: wrong size, unknown/repeated words, or already solved."""


class InvalidPuzzleError(ConnectionsError):
    """A puzzle definition is internally inconsistent."""


class GameOverError(ConnectionsError):
    """An action was attempted on a finished puzzle."""
