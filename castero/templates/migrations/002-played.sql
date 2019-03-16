PRAGMA user_version=2;

alter table episode add column played bit not null default 0;