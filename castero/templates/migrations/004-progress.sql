PRAGMA user_version=4;

create table progress (
    ep_id integer primary key,
		time integer,
    FOREIGN KEY (ep_id) REFERENCES episode(id) ON DELETE CASCADE
);
