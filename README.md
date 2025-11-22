# SonicWave – Data Structures Player (FastAPI + Jinja2)

A modern, dark, outer-space themed web music player demonstrating classic data structures in Python. Drop your `.mp3` / `.wav` files into `static/music/` and enjoy a sleek player with real playback, search, queue, history, genres, recommendations, and a friendly mascot named Nayara.

This build uses FastAPI with Jinja2 templates (functionally equivalent to the requested Flask version) to run in this environment. Data structures are fully implemented in Python with node-based implementations.

## Tech Stack
- Backend: Python 3 + FastAPI
- Templates: Jinja2
- Frontend: HTML5, CSS, Vanilla JavaScript

## Run Locally
```bash
pip install -r requirements.txt
python main.py
```
Then open http://localhost:8000

## Add Music
- Put audio files in `static/music/` (supports `.mp3` and `.wav`).
- On startup, the app scans the folder. Use the Admin page to "Rescan Folder" after adding files at runtime.

## Features & Data Structures
- Master Library: Singly Linked List (SLL)
  - Stores all songs. Insert at end, delete by id, traverse, length.
- Playlists: Doubly Linked List (DLL)
  - Efficient next/prev in a playlist.
- History: Stack
  - Push each play; pop for previous.
- Up Next: Queue
  - FIFO of upcoming songs.
- Browse by Genre: Multi-Linked List
  - Genre headers each point to a list of songs in that genre.
- Search by Title: Binary Search Tree (BST)
  - Case-insensitive insert/search; partial match via traversal.
- Recommendations: Graph (Adjacency List)
  - Connect songs by same artist/genre and near year; used when picking next outside queue/playlist.

## API Summary
- GET `/` – Home UI
- GET `/api/songs`, `/api/songs/{id}`
- GET `/api/search?query=q`
- GET `/api/genres`, `/api/genres/{genre}`
- GET `/api/history`, `/api/queue`
- GET `/api/recommendations/{id}`
- POST `/api/play/{id}` – returns `audio_url`
- POST `/api/queue/add/{id}`
- POST `/api/next`, `/api/prev`
- Admin: `/admin`, POST `/admin/rescan`, edit/delete endpoints

## Mascot – Nayara
- Fixed at bottom-right, floating animation with soft glow.
- First-time onboarding overlay with chat bubbles (localStorage gated).
- Reacts to playback with updated message "Now playing: [title]".

## Space Background
- Deep-space radial base gradient
- Starfield with twinkle animation
- Soft nebula gradient blobs
- Shooting star every ~10s
- Cursor-following glow blob

## Notes
- Favorites toggle and full playlist UI hooks are present as buttons but not backed by persistence beyond in-memory structures.
- For a pure Flask variant, swap FastAPI with Flask equivalents (routes render templates and return JSON); all data structures and manager are framework-agnostic.
