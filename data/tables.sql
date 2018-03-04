CREATE TABLE chatlog (
  id           serial  PRIMARY KEY,
  member_id    bigint,
  message      text,
  timestamp    timestamp,
  server_id    bigint
);