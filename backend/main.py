import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from models import ScoreSubmission, LeaderboardEntry

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:5500,https://abduawais.github.io"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Corporate Ladder Leaderboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard():
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, score, rank, words, streak, updated_at "
        "FROM leaderboard ORDER BY score DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/leaderboard", response_model=LeaderboardEntry)
def submit_score(entry: ScoreSubmission):
    conn = get_connection()
    # Check for existing entry (COLLATE NOCASE handles case-insensitivity)
    existing = conn.execute(
        "SELECT id, score FROM leaderboard WHERE name = ? COLLATE NOCASE",
        (entry.name,),
    ).fetchone()

    if existing:
        if entry.score > existing["score"]:
            conn.execute(
                "UPDATE leaderboard SET score=?, rank=?, words=?, streak=?, "
                "updated_at=datetime('now') WHERE id=?",
                (entry.score, entry.rank, entry.words, entry.streak, existing["id"]),
            )
            conn.commit()
        else:
            # Score not higher — return existing entry unchanged
            row = conn.execute(
                "SELECT name, score, rank, words, streak, updated_at "
                "FROM leaderboard WHERE id=?",
                (existing["id"],),
            ).fetchone()
            conn.close()
            return dict(row)
    else:
        conn.execute(
            "INSERT INTO leaderboard (name, score, rank, words, streak) "
            "VALUES (?, ?, ?, ?, ?)",
            (entry.name, entry.score, entry.rank, entry.words, entry.streak),
        )
        conn.commit()

    row = conn.execute(
        "SELECT name, score, rank, words, streak, updated_at "
        "FROM leaderboard WHERE name = ? COLLATE NOCASE",
        (entry.name,),
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=500, detail="Failed to retrieve saved entry")

    return dict(row)
