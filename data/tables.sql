CREATE TABLE chatlog (
  id           serial PRIMARY KEY,
  member_id    bigint,
  message      text,
  timestamp    timestamp,
  server_id    bigint
);
CREATE TABLE tags (
  id          serial PRIMARY KEY,
  member_id   bigint,
  tag_id      text,
  tag_content text,
  timestamp   timestamp,
  server_id   bigint,
  UNIQUE(tag_id, server_id)
);