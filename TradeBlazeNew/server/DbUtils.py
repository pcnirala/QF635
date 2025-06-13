import sqlite3
import threading

import bcrypt
import sqlite3
import Config


# WAL (Write-Ahead Logging) is a journal mode in SQLite
# designed for fast, safe, concurrent writes
# especially important in low-latency applications.
class WALCounter:
    def __init__(self, counter_name="DEFAULT_SEQ"):
        self._counter_name = counter_name
        self._lock = threading.Lock()

        self._conn = sqlite3.connect(Config.DB_COUNTER_PATH, isolation_level=None, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode
        self._conn.execute("PRAGMA synchronous=NORMAL;")  # Faster syncs
        self._init_table()

    def _init_table(self):
        self._conn.execute("""
                           CREATE TABLE IF NOT EXISTS counters
                           (
                               name
                               TEXT
                               PRIMARY
                               KEY,
                               value
                               INTEGER
                               NOT
                               NULL
                           );
                           """)

        if self._counter_name == 'ORDER_SEQ':
            counter_value = Config.ORDER_SEQ_START
        elif self._counter_name == 'TRADE_SEQ':
            counter_value = Config.TRADE_SEQ_START
        else:
            counter_value = Config.DEFAULT_SEQ_START

        self._conn.execute("""
                           INSERT
                           OR IGNORE INTO counters (name, value) VALUES (?, ?);
                           """, (self._counter_name, counter_value))

    def next(self):
        with self._lock:
            self._conn.execute("""
                               UPDATE counters
                               SET value = value + 1
                               WHERE name = ?;
                               """, (self._counter_name,))
            cursor = self._conn.execute("""
                                        SELECT value
                                        FROM counters
                                        WHERE name = ?;
                                        """, (self._counter_name,))
            return cursor.fetchone()[0]

# run one time to setup users
def set_up_users_db():
    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       username
                       TEXT
                       PRIMARY
                       KEY,
                       hashed_password
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    # Example user creation
    username = "admin"
    password = "secret"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    cursor.execute("INSERT OR REPLACE INTO users (username, hashed_password) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Setting up users db")
    set_up_users_db()
    print("Users db setup complete")
