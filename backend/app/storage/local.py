# app/storage/local.py

"""
Local file storage implementation.

Stores files inside a local folder.
"""

from pathlib import Path
from typing import BinaryIO, Optional
from app.storage.base import StorageBackend


class LocalStorage(StorageBackend):

    def __init__(self, root: str):
        # Root directory where files will be stored
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, key: str) -> Path:
        """
        Converts file key to full file path.
        """
        return self.root / key

    async def put(self, key: str, content: BinaryIO, content_type: str = "") -> str:
        """
        Save file to disk.
        """
        path = self._resolve_path(key)

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Read file content and write to disk
        data = content.read()
        with open(path, "wb") as f:
            f.write(data)

        return key

    async def get(self, key: str) -> Optional[bytes]:
        """
        Read file from disk.
        """
        path = self._resolve_path(key)

        if not path.exists():
            return None

        return path.read_bytes()

    async def delete(self, key: str) -> bool:
        """
        Delete file from disk.
        """
        path = self._resolve_path(key)

        if not path.exists():
            return False

        path.unlink()
        return True