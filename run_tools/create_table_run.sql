-- creation runs table
DROP TABLE runs;

CREATE TABLE runs(
	run_id INTEGER PRIMARY KEY,
	begin_time TEXT NOT NULL,
	end_time TEXT NOT NULL,
    comment TEXT NOT NULL
);