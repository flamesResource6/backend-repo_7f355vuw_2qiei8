"""
Custom data structures used across SonicWave – Data Structures Player.
All structures are node-based and include basic operations with notes on time complexity.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional, List, Dict

# -------------------------------
# Singly Linked List (SLL)
# -------------------------------

@dataclass
class SLLNode:
    data: Any
    next: Optional["SLLNode"] = None


class SinglyLinkedList:
    """Singly Linked List storing the master library of songs.

    Operations:
      - insert at end: O(n)
      - delete by predicate (e.g., song_id): O(n)
      - traverse: O(n)
      - length: O(n)
    """

    def __init__(self):
        self.head: Optional[SLLNode] = None

    def append(self, data: Any) -> None:
        if not self.head:
            self.head = SLLNode(data)
            return
        node = self.head
        while node.next:
            node = node.next
        node.next = SLLNode(data)

    def remove(self, predicate: Callable[[Any], bool]) -> bool:
        prev = None
        node = self.head
        while node:
            if predicate(node.data):
                if prev:
                    prev.next = node.next
                else:
                    self.head = node.next
                return True
            prev = node
            node = node.next
        return False

    def to_list(self) -> List[Any]:
        out = []
        node = self.head
        while node:
            out.append(node.data)
            node = node.next
        return out

    def __len__(self) -> int:
        cnt = 0
        node = self.head
        while node:
            cnt += 1
            node = node.next
        return cnt


# -------------------------------
# Doubly Linked List (DLL)
# -------------------------------

@dataclass
class DLLNode:
    data: Any
    prev: Optional["DLLNode"] = None
    next: Optional["DLLNode"] = None


class DoublyLinkedList:
    """Doubly Linked List supporting efficient next/prev traversal.

    Operations:
      - append: O(1)
      - remove by predicate: O(n)
      - traverse: O(n)
    """

    def __init__(self):
        self.head: Optional[DLLNode] = None
        self.tail: Optional[DLLNode] = None

    def append(self, data: Any) -> None:
        node = DLLNode(data)
        if not self.head:
            self.head = self.tail = node
            return
        assert self.tail is not None
        node.prev = self.tail
        self.tail.next = node
        self.tail = node

    def remove(self, predicate: Callable[[Any], bool]) -> bool:
        node = self.head
        while node:
            if predicate(node.data):
                if node.prev:
                    node.prev.next = node.next
                else:
                    self.head = node.next
                if node.next:
                    node.next.prev = node.prev
                else:
                    self.tail = node.prev
                return True
            node = node.next
        return False

    def to_list(self) -> List[Any]:
        out = []
        node = self.head
        while node:
            out.append(node.data)
            node = node.next
        return out


# -------------------------------
# Stack
# -------------------------------

class Stack:
    """Classic LIFO stack for listening history.

    Operations: push O(1), pop O(1), peek O(1)
    """

    def __init__(self) -> None:
        self._top: Optional[SLLNode] = None

    def push(self, data: Any) -> None:
        node = SLLNode(data, next=self._top)
        self._top = node

    def pop(self) -> Optional[Any]:
        if not self._top:
            return None
        data = self._top.data
        self._top = self._top.next
        return data

    def peek(self) -> Optional[Any]:
        return self._top.data if self._top else None

    def is_empty(self) -> bool:
        return self._top is None

    def to_list(self) -> List[Any]:
        out = []
        node = self._top
        while node:
            out.append(node.data)
            node = node.next
        return out


# -------------------------------
# Queue
# -------------------------------

class Queue:
    """FIFO queue for the Up Next queue.

    Operations: enqueue O(1), dequeue O(1), peek O(1)
    """

    def __init__(self) -> None:
        self._head: Optional[SLLNode] = None
        self._tail: Optional[SLLNode] = None

    def enqueue(self, data: Any) -> None:
        node = SLLNode(data)
        if not self._head:
            self._head = self._tail = node
            return
        assert self._tail is not None
        self._tail.next = node
        self._tail = node

    def dequeue(self) -> Optional[Any]:
        if not self._head:
            return None
        data = self._head.data
        self._head = self._head.next
        if not self._head:
            self._tail = None
        return data

    def peek(self) -> Optional[Any]:
        return self._head.data if self._head else None

    def is_empty(self) -> bool:
        return self._head is None

    def to_list(self) -> List[Any]:
        out = []
        node = self._head
        while node:
            out.append(node.data)
            node = node.next
        return out


# -------------------------------
# Multi Linked List by Genre
# -------------------------------

@dataclass
class GenreSongNode:
    song: Any
    next_song_in_genre: Optional["GenreSongNode"] = None

@dataclass
class GenreHeader:
    genre: str
    first_song: Optional[GenreSongNode] = None
    next_genre: Optional["GenreHeader"] = None


class GenreMultiList:
    """A multi-linked list keyed by genre.

    Genres are a linked list; each points to its own song sub-list.
    Insert/search per genre is O(g + k) where g genres traversed and k songs within genre.
    """

    def __init__(self) -> None:
        self.head: Optional[GenreHeader] = None

    def _find_genre(self, genre: str) -> Optional[GenreHeader]:
        node = self.head
        while node:
            if node.genre.lower() == genre.lower():
                return node
            node = node.next_genre
        return None

    def add_song(self, genre: str, song: Any) -> None:
        header = self._find_genre(genre)
        if not header:
            header = GenreHeader(genre=genre)
            header.next_genre = self.head
            self.head = header
        # prepend into song list for O(1)
        header.first_song = GenreSongNode(song=song, next_song_in_genre=header.first_song)

    def remove_song(self, genre: str, predicate: Callable[[Any], bool]) -> bool:
        header = self._find_genre(genre)
        if not header:
            return False
        prev = None
        node = header.first_song
        while node:
            if predicate(node.song):
                if prev:
                    prev.next_song_in_genre = node.next_song_in_genre
                else:
                    header.first_song = node.next_song_in_genre
                return True
            prev = node
            node = node.next_song_in_genre
        return False

    def get_genres(self) -> List[str]:
        out: List[str] = []
        node = self.head
        while node:
            out.append(node.genre)
            node = node.next_genre
        return sorted(out, key=lambda s: s.lower())

    def get_songs(self, genre: str) -> List[Any]:
        header = self._find_genre(genre)
        out: List[Any] = []
        node = header.first_song if header else None
        while node:
            out.append(node.song)
            node = node.next_song_in_genre
        return out


# -------------------------------
# Binary Search Tree by Title
# -------------------------------

@dataclass
class BSTNode:
    key: str
    value: Any
    left: Optional["BSTNode"] = None
    right: Optional["BSTNode"] = None


class BST:
    """Case-insensitive BST keyed by song title.

    insert/search average O(log n), worst O(n) if unbalanced.
    """

    def __init__(self) -> None:
        self.root: Optional[BSTNode] = None

    def insert(self, key: str, value: Any) -> None:
        k = key.lower()
        self.root = self._insert(self.root, k, value)

    def _insert(self, node: Optional[BSTNode], key: str, value: Any) -> BSTNode:
        if not node:
            return BSTNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
        return node

    def search(self, key: str) -> Optional[Any]:
        k = key.lower()
        node = self.root
        while node:
            if k < node.key:
                node = node.left
            elif k > node.key:
                node = node.right
            else:
                return node.value
        return None

    def inorder(self) -> List[Any]:
        out: List[Any] = []
        def _in(n: Optional[BSTNode]):
            if not n:
                return
            _in(n.left)
            out.append(n.value)
            _in(n.right)
        _in(self.root)
        return out

    def partial_match(self, query: str) -> List[Any]:
        q = query.lower()
        out: List[Any] = []
        def _traverse(n: Optional[BSTNode]):
            if not n:
                return
            if q in n.key:
                out.append(n.value)
            _traverse(n.left)
            _traverse(n.right)
        _traverse(self.root)
        return out


# -------------------------------
# Graph (Adjacency List)
# -------------------------------

class SongGraph:
    """Graph using adjacency list: song_id -> list of similar song_ids.

    Building edges is O(n^2) naive based on similarity heuristics.
    Lookup neighbors is O(1) average per song id.
    """

    def __init__(self) -> None:
        self.adj: Dict[int, List[int]] = {}

    def add_song(self, song_id: int) -> None:
        self.adj.setdefault(song_id, [])

    def add_edge(self, a: int, b: int) -> None:
        if a == b:
            return
        self.adj.setdefault(a, [])
        self.adj.setdefault(b, [])
        if b not in self.adj[a]:
            self.adj[a].append(b)
        if a not in self.adj[b]:
            self.adj[b].append(a)

    def neighbors(self, song_id: int) -> List[int]:
        return list(self.adj.get(song_id, []))

    def remove_song(self, song_id: int) -> None:
        if song_id in self.adj:
            for n in list(self.adj[song_id]):
                if song_id in self.adj.get(n, []):
                    self.adj[n].remove(song_id)
            del self.adj[song_id]
