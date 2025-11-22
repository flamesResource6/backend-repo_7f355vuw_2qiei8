import os
import random
from typing import Dict, List, Optional

from models import Song, Playlist
from data_structures import (
    SinglyLinkedList,
    GenreMultiList,
    BST,
    Queue,
    Stack,
    SongGraph,
)


class MusicLibraryManager:
    """Coordinates data structures and provides high-level operations.

    - Scans music dir for .mp3/.wav
    - Inserts songs into SLL (master lib), Genre Multi-List, BST, Graph
    - Maintains global Queue (Up Next) and Stack (History)
    """

    def __init__(self, music_dir: str = "static/music") -> None:
        self.music_dir = music_dir
        self.library = SinglyLinkedList()  # master SLL
        self.genres = GenreMultiList()
        self.bst = BST()
        self.queue = Queue()
        self.history = Stack()
        self.graph = SongGraph()
        self.playlists: Dict[str, Playlist] = {}
        self._song_index: Dict[int, Song] = {}
        self._next_id = 1
        self.rescan()

    # -----------------------
    # Scanning & building
    # -----------------------
    def rescan(self) -> None:
        """Scan the music directory, rebuild structures from scratch."""
        # Reset
        self.library = SinglyLinkedList()
        self.genres = GenreMultiList()
        self.bst = BST()
        self.graph = SongGraph()
        self._song_index = {}
        self._next_id = 1

        # Load files
        for fname in sorted(os.listdir(self.music_dir)):
            if not (fname.lower().endswith(".mp3") or fname.lower().endswith(".wav")):
                continue
            file_path = os.path.join("static", "music", fname)
            base = os.path.splitext(fname)[0]
            # Naive metadata from filename: Title - Artist or Title
            title = base.replace("_", " ")
            artist = "Unknown"
            album = "Unknown"
            genre = "Unknown"
            year = 2024
            duration_seconds = 0
            song = Song(
                song_id=self._next_id,
                title=title,
                artist=artist,
                album=album,
                genre=genre,
                year=year,
                duration_seconds=duration_seconds,
                file_path=file_path,
                play_count=0,
                is_favorite=False,
            )
            self._index_and_insert(song)
            self._next_id += 1

        # Build similarity edges (naive O(n^2))
        all_songs = self.get_all_songs()
        for i in range(len(all_songs)):
            a = all_songs[i]
            for j in range(i + 1, len(all_songs)):
                b = all_songs[j]
                score = 0
                if a.artist and b.artist and a.artist == b.artist:
                    score += 3
                if a.genre and b.genre and a.genre == b.genre:
                    score += 2
                if abs(a.year - b.year) <= 2:
                    score += 1
                if score >= 2:
                    self.graph.add_edge(a.song_id, b.song_id)

    def _index_and_insert(self, song: Song) -> None:
        self._song_index[song.song_id] = song
        self.library.append(song)
        self.genres.add_song(song.genre or "Unknown", song)
        self.bst.insert(song.title or str(song.song_id), song)
        self.graph.add_song(song.song_id)

    # -----------------------
    # Library
    # -----------------------
    def get_all_songs(self) -> List[Song]:
        return self.library.to_list()

    def get_song_by_id(self, song_id: int) -> Optional[Song]:
        return self._song_index.get(song_id)

    def update_song(self, song_id: int, **fields) -> None:
        song = self._song_index.get(song_id)
        if not song:
            return
        old_genre = song.genre
        old_title = song.title
        for k, v in fields.items():
            if v is None:
                continue
            if hasattr(song, k):
                setattr(song, k, v)
        # update genre multilist if changed
        if old_genre != song.genre:
            self.genres.remove_song(old_genre, lambda s: s.song_id == song_id)
            self.genres.add_song(song.genre, song)
        # update BST if title changed
        if old_title != song.title:
            # Easiest: rebuild BST for correctness
            self.bst = BST()
            for s in self.get_all_songs():
                self.bst.insert(s.title or str(s.song_id), s)
        # graph could be recomputed lazily; keep simple and rebuild small neighborhood
        # For simplicity in this project: leave as-is or rebuild fully on rescan.

    def delete_song(self, song_id: int) -> None:
        song = self._song_index.get(song_id)
        if not song:
            return
        # remove from SLL
        self.library.remove(lambda s: s.song_id == song_id)
        # genre list
        self.genres.remove_song(song.genre, lambda s: s.song_id == song_id)
        # bst rebuild
        del self._song_index[song_id]
        self.bst = BST()
        for s in self.get_all_songs():
            self.bst.insert(s.title or str(s.song_id), s)
        # queue cleanup
        new_q = Queue()
        for s in self.queue.to_list():
            if s.song_id != song_id:
                new_q.enqueue(s)
        self.queue = new_q
        # history cleanup
        new_hist = Stack()
        for s in reversed(self.history.to_list()):
            if s.song_id != song_id:
                new_hist.push(s)
        self.history = new_hist
        # playlists cleanup
        for pl in self.playlists.values():
            pl.remove_by_id(song_id)
        # graph cleanup
        self.graph.remove_song(song_id)

    # -----------------------
    # Favorites
    # -----------------------
    def toggle_favorite(self, song_id: int) -> Optional[bool]:
        song = self._song_index.get(song_id)
        if not song:
            return None
        song.is_favorite = not song.is_favorite
        return song.is_favorite

    def get_favorites(self) -> List[Song]:
        return [s for s in self.get_all_songs() if s.is_favorite]

    # -----------------------
    # Genres
    # -----------------------
    def get_all_genres(self) -> List[str]:
        return self.genres.get_genres()

    def get_songs_by_genre(self, genre: str) -> List[Song]:
        return self.genres.get_songs(genre)

    # -----------------------
    # Search (BST)
    # -----------------------
    def search_by_title(self, query: str) -> List[Song]:
        exact = self.bst.search(query)
        if exact:
            return [exact]
        return self.bst.partial_match(query)

    # -----------------------
    # Playlists (DLL wrapper in Playlist)
    # -----------------------
    def create_playlist(self, name: str) -> None:
        if name not in self.playlists:
            self.playlists[name] = Playlist(name)

    def delete_playlist(self, name: str) -> None:
        if name in self.playlists:
            del self.playlists[name]

    def list_playlists(self) -> List[str]:
        return sorted(self.playlists.keys(), key=lambda s: s.lower())

    def add_song_to_playlist(self, name: str, song_id: int) -> None:
        self.create_playlist(name)
        song = self.get_song_by_id(song_id)
        if song:
            self.playlists[name].add(song)

    def remove_song_from_playlist(self, name: str, song_id: int) -> None:
        if name in self.playlists:
            self.playlists[name].remove_by_id(song_id)

    def get_playlist_songs(self, name: str) -> List[Song]:
        if name in self.playlists:
            return self.playlists[name].to_list()
        return []

    # -----------------------
    # Queue
    # -----------------------
    def enqueue_song(self, song_id: int) -> None:
        song = self.get_song_by_id(song_id)
        if song:
            self.queue.enqueue(song)

    def dequeue_song(self) -> Optional[Song]:
        return self.queue.dequeue()

    def get_queue_list(self) -> List[Song]:
        return self.queue.to_list()

    # -----------------------
    # History
    # -----------------------
    def record_play(self, song: Song) -> None:
        song.play_count += 1
        self.history.push(song)

    def get_history_list(self, limit: int = 20) -> List[Song]:
        return self.history.to_list()[:limit]

    # -----------------------
    # Graph recommendation
    # -----------------------
    def get_similar_songs(self, song_id: int) -> List[int]:
        return self.graph.neighbors(song_id)

    def get_next_similar_song(self, song_id: int) -> Optional[Song]:
        neighbors = self.graph.neighbors(song_id)
        random.shuffle(neighbors)
        for nid in neighbors:
            s = self.get_song_by_id(nid)
            if s:
                return s
        # fallback random
        all_songs = self.get_all_songs()
        return random.choice(all_songs) if all_songs else None

    # -----------------------
    # Playback helpers
    # -----------------------
    def get_next_song(self, current_song_id: Optional[int], current_playlist_name: Optional[str]) -> Optional[Song]:
        # Priority: playlist next -> queue -> graph similar -> random
        if current_playlist_name and current_playlist_name in self.playlists and current_song_id:
            nxt = self.playlists[current_playlist_name].next_of(current_song_id)
            if nxt:
                return nxt
        # queue
        q = self.dequeue_song()
        if q:
            return q
        # graph
        if current_song_id:
            s = self.get_next_similar_song(current_song_id)
            if s:
                return s
        # random fallback
        all_songs = self.get_all_songs()
        return random.choice(all_songs) if all_songs else None

    def get_previous_song(self, current_song_id: Optional[int], current_playlist_name: Optional[str]) -> Optional[Song]:
        # Priority: playlist prev -> history top (excluding current)
        if current_playlist_name and current_playlist_name in self.playlists and current_song_id:
            prv = self.playlists[current_playlist_name].prev_of(current_song_id)
            if prv:
                return prv
        # history previous (pop current if present)
        top = self.history.pop()
        if top and current_song_id and top.song_id == current_song_id:
            # pop one more for previous
            return self.history.pop()
        return top
