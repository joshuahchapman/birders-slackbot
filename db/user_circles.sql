create table user_circles (
    id serial primary key,
    user_id varchar(20),
    latitude decimal(15,10),
    longitude decimal(15,10),
    user_circle_name varchar(100),
    radius_km int,
    created_at timestamp,
    updated_at timestamp,
    deleted smallint
);

create index idx_user_circles_user_radius 
on user_circles(user_id, radius_km);
