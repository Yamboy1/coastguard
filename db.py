from collections.abc import Sequence
from dataclasses import dataclass
from enum import IntFlag
import sqlite3
from flask import g, current_app
import click

DATABASE = "./coastguard.db"


class Medals(IntFlag):
    CASTAWAY = 2
    SECOONDARYMISSION = 4


@dataclass
class LevelScore:
    level: int
    score: int
    medals: Medals


@dataclass
class GameInfo:
    username: str
    levels: list[LevelScore]
    levelsunlocked: int = 0
    currentrank: int = 0
    totalscore: int = 0


def get_db() -> sqlite3.Connection:
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row

    return db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def load_scores(username: str = "USERNAME") -> GameInfo:
    with get_db() as conn:
        data: sqlite3.Row | None = conn.execute(
            "SELECT * FROM data WHERE username = ?",
            (username,),
        ).fetchone()

        levels: list[sqlite3.Row] = conn.execute(
            "SELECT * FROM levels WHERE username = ?",
            (username,),
        ).fetchall()

        if not data:
            return GameInfo(username, levels=[])

        return GameInfo(
            username=username,
            levelsunlocked=data["levelsunlocked"],
            currentrank=data["currentrank"],
            totalscore=data["totalscore"],
            levels=[
                LevelScore(
                    level=level_data["level"],
                    score=level_data["score"],
                    medals=Medals(level_data["medals"]),
                )
                for level_data in levels
            ],
        )


def save_scores(game_info: GameInfo):
    with get_db() as conn:
        conn.execute(
            "UPDATE data SET levelsunlocked = ?, currentrank = ?, totalscore = ? WHERE username = ?",
            (
                game_info.levelsunlocked,
                game_info.currentrank,
                game_info.totalscore,
                game_info.username,
            ),
        )

        conn.executemany(
            "UPDATE levels SET medals = ?, score = ? WHERE level = ? AND username = ?",
            (
                (
                    level_data.medals,
                    level_data.score,
                    level_data.level,
                    game_info.username,
                )
                for level_data in game_info.levels
            ),
        )


def init_scores(username: str):
    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO data (username) VALUES (?)",
            (username,),
        )

        conn.executemany(
            "INSERT OR IGNORE into levels (username, level) VALUES (?, ?)",
            ((username, level) for level in range(1, 13)),
        )


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
