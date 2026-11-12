from sqlalchemy import text
from sqlalchemy.engine import Engine

USER_FACE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("face_enrolled", "BOOLEAN NOT NULL DEFAULT 0"),
    ("face_enrolled_at", "DATETIME"),
    ("face_image_path", "VARCHAR(255)"),
    ("face_embedding_path", "VARCHAR(255)"),
)


def ensure_schema(engine: Engine) -> None:
    _ensure_user_face_columns(engine)


def _ensure_user_face_columns(engine: Engine) -> None:
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        existing = {row[1] for row in rows}
        for name, definition in USER_FACE_COLUMNS:
            if name in existing:
                continue
            conn.execute(
                text(f"ALTER TABLE users ADD COLUMN {name} {definition}"),
            )
