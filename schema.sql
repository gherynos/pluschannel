CREATE TABLE feeds(

    pkey TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    inserted NUMERIC,
    photo_url TEXT
);