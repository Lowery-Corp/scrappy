class ScrappyError(RuntimeError):
    """Base class for expected application failures."""


class StorageOperationError(ScrappyError):
    """Raised when object storage or file-store persistence fails."""


class ResourceProvisioningError(ScrappyError):
    """Raised when initial resources cannot be created for a user."""


class OwnershipError(ScrappyError):
    """Raised when a request references a resource owned by another user."""
