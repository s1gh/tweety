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
CREATE TABLE custom_command (
  id            serial PRIMARY KEY,
  member_id     bigint,
  trigger_word  text,
  trigger_text  text,
  timestamp     timestamp,
  server_id     bigint,
  UNIQUE(trigger_word, server_id)
)