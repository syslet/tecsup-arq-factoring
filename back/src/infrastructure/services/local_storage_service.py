import os

from src.domain.repositories.storage_repository import IStorageService


class LocalStorageService(IStorageService):
    """Local filesystem storage implementation for Docker volume persistence."""

    def __init__(self, base_dir: str | None = None) -> None:
        if base_dir:
            self.base_dir = base_dir
        else:
            env_dir = os.getenv("UPLOAD_DIR")
            if env_dir:
                self.base_dir = env_dir
            elif os.path.exists("/app") and os.access("/app", os.W_OK):
                self.base_dir = "/app/uploads"
            else:
                self.base_dir = os.path.abspath("storage_data")

        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)

    def save_file(self, file_bytes: bytes, filename: str, subfolder: str = "") -> str:
        target_dir = os.path.join(self.base_dir, subfolder) if subfolder else self.base_dir
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return filename

    def get_file_path(self, filename: str, subfolder: str = "") -> str:
        target_dir = os.path.join(self.base_dir, subfolder) if subfolder else self.base_dir
        return os.path.join(target_dir, filename)
