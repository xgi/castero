PRAGMA user_version=3;

create table queue (
    id integer primary key,
    ep_id integer,
    FOREIGN KEY (ep_id) REFERENCES episode(id) ON DELETE CASCADE
);