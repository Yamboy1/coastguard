-- sqlfluff:dialect:sqlite

CREATE TABLE IF NOT EXISTS data (
    username text PRIMARY KEY NOT NULL,
    levelsunlocked int NOT NULL DEFAULT 0,
    currentrank int NOT NULL DEFAULT 0,
    totalscore int NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS levels (
    username text NOT NULL,
    level int NOT NULL,
    score int NOT NULL DEFAULT 0,
    medals int NOT NULL DEFAULT 0,
    PRIMARY KEY (username, level)
);
