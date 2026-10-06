CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE readings (
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    hr REAL NOT NULL,
    acc REAL NOT NULL,
    label INTEGER NOT NULL DEFAULT 0,
    anomaly_type TEXT NOT NULL DEFAULT 'normal',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_readings_user_time ON readings(user_id,timestamp);

CREATE TABLE alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reading_id INTEGER,
    timestamp DATETIME NOT NULL,
    anomaly_type TEXT NOT NULL,
    anomaly_score REAL,
    message TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (reading_id) REFERENCES readings(reading_id)
);

CREATE INDEX idx_alerts_user_time ON alerts(user_id,timestamp);
