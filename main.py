import os
import random
from typing import Optional, Dict, List
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

# Import our library manager and models
# We'll create these files below
from music_manager import MusicLibraryManager

app = FastAPI(title="SonicWave – Data Structures Player")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure folders exist
os.makedirs("static/music", exist_ok=True)
os.makedirs("static/img", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize the music library manager
manager = MusicLibraryManager(music_dir="static/music")


# -----------------------------
# Models for API payloads
# -----------------------------
class PlayRequest(BaseModel):
    playlist_name: Optional[str] = None


# -----------------------------
# Web routes
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    songs = manager.get_all_songs()
    genres = manager.get_all_genres()
    history = manager.get_history_list(limit=10)
    queue = manager.get_queue_list()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "songs": songs,
            "genres": genres,
            "history": history,
            "queue": queue,
            "app_name": "SonicWave",
        },
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    songs = manager.get_all_songs()
    return templates.TemplateResponse(
        "admin.html", {"request": request, "songs": songs, "app_name": "SonicWave"}
    )


# -----------------------------
# API routes – Library
# -----------------------------
@app.get("/api/songs")
async def api_songs():
    return [s.to_dict() for s in manager.get_all_songs()]


@app.get("/api/songs/{song_id}")
async def api_song(song_id: int):
    song = manager.get_song_by_id(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song.to_dict()


@app.get("/api/search")
async def api_search(query: str):
    results = manager.search_by_title(query)
    return [s.to_dict() for s in results]


@app.get("/api/genres")
async def api_genres():
    return manager.get_all_genres()


@app.get("/api/genres/{genre}")
async def api_genre_songs(genre: str):
    songs = manager.get_songs_by_genre(genre)
    return [s.to_dict() for s in songs]


@app.get("/api/history")
async def api_history():
    return [s.to_dict() for s in manager.get_history_list(limit=30)]


@app.get("/api/queue")
async def api_queue():
    return [s.to_dict() for s in manager.get_queue_list()]


@app.get("/api/recommendations/{song_id}")
async def api_recommendations(song_id: int):
    ids = manager.get_similar_songs(song_id)
    return [manager.get_song_by_id(i).to_dict() for i in ids if manager.get_song_by_id(i)]


# -----------------------------
# API routes – Playback
# -----------------------------
@app.post("/api/play/{song_id}")
async def api_play(song_id: int, payload: PlayRequest | None = None):
    song = manager.get_song_by_id(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    manager.record_play(song)
    audio_url = f"/" + song.file_path.replace("\\", "/")
    return {"status": "ok", "song": song.to_dict(), "audio_url": audio_url}


@app.post("/api/queue/add/{song_id}")
async def api_queue_add(song_id: int):
    manager.enqueue_song(song_id)
    return {"status": "ok", "queue": [s.to_dict() for s in manager.get_queue_list()]}


@app.post("/api/next")
async def api_next(current_song_id: Optional[int] = None, current_playlist_name: Optional[str] = None):
    next_song = manager.get_next_song(current_song_id, current_playlist_name)
    if not next_song:
        raise HTTPException(status_code=404, detail="No next song available")
    manager.record_play(next_song)
    return {"status": "ok", "song": next_song.to_dict(), "audio_url": f"/" + next_song.file_path}


@app.post("/api/prev")
async def api_prev(current_song_id: Optional[int] = None, current_playlist_name: Optional[str] = None):
    prev_song = manager.get_previous_song(current_song_id, current_playlist_name)
    if not prev_song:
        raise HTTPException(status_code=404, detail="No previous song available")
    manager.record_play(prev_song)
    return {"status": "ok", "song": prev_song.to_dict(), "audio_url": f"/" + prev_song.file_path}


# -----------------------------
# API routes – Admin
# -----------------------------
@app.post("/admin/login")
async def admin_login(password: str = Form(...)):
    if password == os.getenv("ADMIN_PASSWORD", "sonicwave123"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    raise HTTPException(status_code=403, detail="Invalid password")


@app.post("/admin/songs/{song_id}/edit")
async def admin_edit_song(song_id: int, title: str = Form(None), artist: str = Form(None), album: str = Form(None), genre: str = Form(None), year: int = Form(None)):
    manager.update_song(song_id, title=title, artist=artist, album=album, genre=genre, year=year)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/admin/songs/{song_id}/delete")
async def admin_delete_song(song_id: int):
    manager.delete_song(song_id)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/admin/rescan")
async def admin_rescan():
    manager.rescan()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


# Simple health endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "songs": len(manager.get_all_songs())}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
