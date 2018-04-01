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
);
CREATE TABLE members (
  id          serial PRIMARY KEY,
  member_id   bigint,
  last_played timestamp,
  server_id   bigint,
  UNIQUE(member_id, server_id)
);
CREATE TABLE games (
  id        serial PRIMARY KEY,
  member_id bigint,
  server_id bigint,
  game      text,
  game_time int,
  timestamp timestamp
);
CREATE TABLE quotes (
  id        serial PRIMARY KEY,
  added_by  bigint,
  server_id bigint,
  quote     text,
  author    text,
  timestamp timestamp,
  UNIQUE(author, quote, server_id)
);
CREATE TABLE reminders (
  id        serial PRIMARY KEY,
  member    bigint,
  server_id bigint,
  reminder  text,
  timestamp timestamp,
  UNIQUE(member, server_id)
);