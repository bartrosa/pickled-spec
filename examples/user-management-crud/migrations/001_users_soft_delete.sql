CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    consent_marketing INTEGER NOT NULL DEFAULT 0,
    consent_at TEXT NOT NULL DEFAULT (datetime('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at TEXT NULL,
    hard_delete_after TEXT NULL
);

CREATE INDEX idx_users_deleted_at ON users(deleted_at);

CREATE INDEX idx_users_hard_delete_after ON users(hard_delete_after);

CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    occurred_at TEXT NOT NULL DEFAULT (datetime('now')),
    payload TEXT
);
