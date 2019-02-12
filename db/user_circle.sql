CREATE TABLE user_circle (
	user_circle_id serial NOT NULL PRIMARY KEY,
	user_id varchar(20) NOT NULL,
	latitude numeric(15,10) NOT NULL,
	longitude numeric(15,10) NOT NULL,
	user_circle_name varchar(100) NOT NULL DEFAULT '',
	radius_km int4 NOT NULL,
	user_default_circle int2 NOT NULL DEFAULT 0,
	created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	deleted int2 NOT NULL DEFAULT 0,
	UNIQUE (user_id, user_circle_name)
);
