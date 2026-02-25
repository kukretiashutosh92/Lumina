# app/storage/base.py

"""
Abstract storage interface.

Allows us to switch between:
- Local storage
- S3
- Cloud storage

Without changing business logic.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class StorageBackend(ABC):

    @abstractmethod
    async def put(self, key: str, content: BinaryIO, content_type: str = "") -> str:
        """Upload file to storage"""
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> Optional[bytes]:
        """Retrieve file from storage"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete file from storage"""
        raise NotImplementedError