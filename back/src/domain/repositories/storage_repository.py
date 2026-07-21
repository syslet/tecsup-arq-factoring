from abc import ABC, abstractmethod


class IStorageService(ABC):
    """Interface for local or remote file storage operations."""

    @abstractmethod
    def save_file(self, file_bytes: bytes, filename: str, subfolder: str = "") -> str:
        """Saves file bytes to destination and returns the relative path or filename."""
        pass

    @abstractmethod
    def get_file_path(self, filename: str, subfolder: str = "") -> str:
        """Returns the absolute file path for retrieval."""
        pass
