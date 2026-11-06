import threading


class AvatarTaken(Exception):
    pass


class Store:
    """Quiz profiles live only in this process's memory. Nothing touches disk."""

    def __init__(self):
        self._profiles: dict[str, dict] = {}
        self._lock = threading.Lock()

    def taken(self) -> set[str]:
        with self._lock:
            return set(self._profiles)

    def add(self, avatar: str, profile: dict) -> None:
        with self._lock:
            if avatar in self._profiles:
                raise AvatarTaken(avatar)
            self._profiles[avatar] = profile

    def all(self) -> list[dict]:
        with self._lock:
            return list(self._profiles.values())

    def count(self) -> int:
        with self._lock:
            return len(self._profiles)

    def clear(self) -> int:
        with self._lock:
            n = len(self._profiles)
            self._profiles.clear()
            return n
