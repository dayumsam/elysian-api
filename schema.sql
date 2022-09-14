DROP TABLE IF EXISTS styles;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS suggestion;
DROP TABLE IF EXISTS contact;

CREATE TABLE styles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    styles VARCHAR(50),
    similarities INT,
    time_period INT,
    functionality INT,
    traffic INT,
    horizontal INT,
    vertical INT,
    dynamic INT,
    shape INT,
    details INT,
    orientation INT,
    lighting INT,
    intensity INT,
    fixtures INT,
    vibrancy INT,
    statement INT,
    tone INT,
    finish INT,
    feel INT,
    ambience INT,
    prints INT,
    style INT
);

CREATE TABLE tags(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50)
);

CREATE TABLE images(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id VARCHAR(50),
    url VARCHAR(500),
    tags VARCHAR(50)
);

