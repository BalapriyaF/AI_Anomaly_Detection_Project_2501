import sqlite3
import pandas as pd

df = pd.read_csv("../setup/readings.csv")
events_df = pd.read_csv("../setup/anomaly_events.csv")

con = sqlite3.connect("wearable.db")
con.executescript(open("schema.sql").read())

con.executemany(
    "INSERT OR IGNORE INTO users(user_id, name) VALUES (?, ?)",
    [(1, "User 1"), (2, "User 2"), (3, "User 3")]
)

for user_id, offset in [(1, 0), (2, 2), (3, 4)]:

    x = df.copy()

    x["timestamp"] = (
        pd.to_datetime(x["timestamp"])
        + pd.to_timedelta(offset, unit="h")
    )

    # Insert all readings
    con.executemany(
        """
        INSERT INTO readings
        (user_id, timestamp, hr, acc, label, anomaly_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                user_id,
                r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                float(r.hr),
                float(r.acc),
                int(r.label),
                r.anomaly_type
            )
            for r in x.itertuples(index=False)
        ]
    )

    # Insert exactly one alert for each of the 20 anomaly events
    for event in events_df.itertuples(index=False):

        start_row = int(event.start_row)

        row = x.iloc[start_row]

        reading_id = con.execute(
            """
            SELECT reading_id
            FROM readings
            WHERE user_id = ? AND timestamp = ?
            """,
            (
                user_id,
                row.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            )
        ).fetchone()[0]

        con.execute(
            """
            INSERT INTO alerts
            (user_id, reading_id, timestamp, anomaly_type,
             anomaly_score, message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                reading_id,
                row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                event.anomaly_type,
                1.0,
                f"{event.anomaly_type} detected"
            )
        )

con.commit()
con.close()

print("Created wearable.db and loaded 3 users.")
print("Inserted readings and 20 anomaly alerts per user.")