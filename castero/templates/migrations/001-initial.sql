PRAGMA user_version=1;

create table feed (
    key             text primary key,
    title           text,
    description     text,
    link            text,
    last_build_date text,
    copyright       text
);

create table episode (
    id          integer primary key,
    feed_key    text,
    title       text,
    description text,
    link        text,
    pubdate     text,
    copyright   text,
    enclosure   text,
    FOREIGN KEY (feed_key) REFERENCES feed(key) ON DELETE CASCADE
);