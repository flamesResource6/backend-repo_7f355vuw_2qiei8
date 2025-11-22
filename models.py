from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Song:
    """Represents a single song's metadata.

    Fields mirror project spec. Provides to_dict helper for JSON.
    """

    song_id: int
    title: str
    artist: str
    album: str
    genre: str
    year: int
    duration_seconds: int
    file_path: str
    play_count: int = 0
    is_favorite: bool = False

    def to_dict(self) -> dict:
        return {
            "song_id": self.song_id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "genre": self.genre,
            "year": self.year,
            "duration_seconds": self.duration_seconds,
            "file_path": self.file_path,
            "play_count": self.play_count,
            "is_favorite": self.is_favorite,
        }


class Playlist:
    """Playlist backed by a Doubly Linked List of Song nodes.

    Provides O(1) next/prev traversal once you have a node reference.
    """

    def __init__(self, name: str):
        self.name = name
        # We store head/tail via DLL implementation (in data_structures)
        from data_structures import DoublyLinkedList

        self.dll = DoublyLinkedList()

    def add(self, song: Song):
        self.dll.append(song)

    def remove_by_id(self, song_id: int) -> bool:
        return self.dll.remove(lambda s: s.song_id == song_id)

    def to_list(self):
        return self.dll.to_list()

    def find_node_index(self, song_id: int) -> int:
        idx = 0
        node = self.dll.head
        while node:
            if node.data.song_id == song_id:
                return idx
            node = node.next
            idx += 1
        return -1

    def next_of(self, song_id: int):
        node = self.dll.head
        while node:
            if node.data.song_id == song_id:
                return node.next.data if node.next else None
            node = node.next
        return None

    def prev_of(self, song_id: int):
        node = self.dll.head
        while node:
            if node.data.song_id == song_id:
                return node.prev.data if node.prev else None
            node = node.next
        return None


class UserSessionState:
    """Holds lightweight session playback context.

    This is a simple container to demonstrate context; not persisted.
    """

    def __init__(self):
        self.current_song_id: Optional[int] = None
        self.current_playlist_name: Optional[str] = None
        self.shuffle: bool = False
        self.repeat: bool = False
