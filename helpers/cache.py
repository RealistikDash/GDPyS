from __future__ import annotations

from typing import Generic
from typing import Hashable
from typing import Optional
from typing import TypeVar

T = TypeVar("T")


class LRUCache(Generic[T]):

    __slots__ = (
        "capacity",
        "_cache",
    )

    def __init__(self, capacity: int = 500) -> None:
        self.capacity = capacity
        self._cache: dict[Hashable, T] = {}

    def __getitem__(self, key: Hashable) -> T:
        return self._cache[key]

    def __setitem__(self, key: Hashable, value: T) -> None:
        self._cache[key] = value
        self._ensure_capacity()

    def __delitem__(self, key: Hashable) -> None:
        del self._cache[key]

    def __contains__(self, key: Hashable) -> bool:
        return key in self._cache

    def __len__(self) -> int:
        return len(self._cache)

    def _ensure_capacity(self) -> None:
        """Ensures that the cache does not exceed its capacity by removing
        the oldest item if it does."""

        cache_iter = iter(self._cache)
        while len(self._cache) > self.capacity:
            del self._cache[next(cache_iter)]

    def get(self, key: Hashable, default: Optional[T] = None) -> Optional[T]:
        return self._cache.get(key, default)

    def cache(self, key: Hashable, value: T) -> None:
        self[key] = value

    def drop(self, key: Hashable) -> None:
        del self[key]

    def get_all_items(self) -> list[T]:
        """Creates a new list of all items in the cache (to avoid any
        concurrency issues)."""
        return list(self._cache.values())
