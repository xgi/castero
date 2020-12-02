PRAGMA user_version=4;

create table progress (
    id integer primary key,
		time integer,
    ep_id integer UNIQUE,
    FOREIGN KEY (ep_id) REFERENCES episode(id) ON DELETE CASCADE
);
