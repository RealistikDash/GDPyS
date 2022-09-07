from __future__ import annotations

from .common import dict_keys
from .time import get_timestamp


class Cache:
    """Cache of objects with IDs."""

    # TODO: The caching system can maybe call a function to automatically cache something without the help of a helper class.

    def __init__(self, cache_length: int = 5, cache_limit: int = 500):
        """Establishes a cache and configures the limits.
        Args:
            cache_length (int): How long (in minutes) each cache lasts before
                being removed
            cache_limit (int): A limit to how many objects can be max cached
                before other objects start being removed.
        """
        self._cache = {}  # The main cache object.
        self.length = (
            cache_length * 60
        )  # Multipled by 60 to get the length in seconds rather than minutes.
        self._cache_limit = cache_limit

    @property
    def cached_items(self) -> int:
        """Returns an int of the lumber of cached items stored."""

        return len(self._cache)

    def __len__(self):
        return self.cached_items()

    def cache(self, cache_id: int, cache_obj: object) -> None:
        """Adds an object to the cache."""
        self._cache[cache_id] = {
            "id": cache_id,
            "expire": get_timestamp() + self.length,
            "object": cache_obj,
        }
        self.run_checks()

    def remove_cache(self, cache_id: int) -> None:
        """Removes an object from cache."""
        try:
            del self._cache[cache_id]
        except KeyError:
            # It doesnt matter if it fails. All that matters is that no such object exist and if it doesnt exist in the first place, that's already objective complete.
            pass

    def get(self, cache_id: int) -> object:
        """Retrieves a cached object from cache."""

        # Try to get it from cache.
        curr_obj = self._cache.get(cache_id)
        if curr_obj is None:
            return None
        return curr_obj["object"]

    def _get_cached_ids(self) -> list:
        """Returns a list of all cache IDs currently cached."""
        return tuple(self._cache)

    def _get_object(self, cache_id: int) -> list:
        """Gets object using set function."""
        raise NotImplementedError(
            "The GDPyS Cache system cannot yet create objects by itself.",
        )
        # return cache_id, object

    def _get_expired_cache(self) -> list:
        """Returns a list of expired cache IDs."""
        current_timestamp = get_timestamp()
        expired = []
        for cache_id in self._get_cached_ids():
            # We dont want to use get as that  will soon have the ability to make its own objects, slowing this down.
            if self._cache[cache_id]["expire"] < current_timestamp:
                # This cache is expired.
                expired.append(cache_id)
        return expired

    def _remove_expired_cache(self) -> None:
        """Removes all of the expired cache."""
        for cache_id in self._get_expired_cache():
            self.remove_cache(cache_id)

    def _remove_limit_cache(self) -> None:
        """Removes all objects past limit if cache reached its limit."""

        # Calculate how much objects we have to throw away.
        throw_away_count = len(self._get_cached_ids()) - self._cache_limit

        if throw_away_count < 1:
            # No levels to throw away
            return

        # Get x oldest ids to remove.
        throw_away_ids = self._get_cached_ids()[:throw_away_count]
        for cache_id in throw_away_ids:
            self.remove_cache(cache_id)

    def run_checks(self) -> None:
        """Runs checks on the cache."""
        self._remove_expired_cache()
        self._remove_limit_cache()

    def get_all_items(self) -> list:
        """Creates a list of all cached items in the order of when it was
        cached."""

        return [obj["object"] for _, obj in self._cache.items()]
