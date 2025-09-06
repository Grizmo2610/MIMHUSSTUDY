import os
import sqlite3
import psycopg2
import uuid


class Database:
    def __init__(self, filename: str = "mydb"):
        env = os.getenv("ENV", "dev")
        self.filename = filename
        if env == "dev":
            self.db_type = "sqlite"
            self.conn = sqlite3.connect(f"{filename}.sqlite3", check_same_thread=False)
        else:
            self.db_type = "postgres"
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
        self.cursor = self.conn.cursor()

    def format_query(self, query: str, params):
        if self.db_type == "sqlite":
            # format placeholder
            query = query.replace("%s", "?")

            # thay kiểu dữ liệu đặc thù
            query = query.replace("UUID", "TEXT")
            query = query.replace("TIMESTAMPTZ", "TEXT")
            query = query.replace("DEFAULT gen_random_uuid()", "")
            query = query.replace("DEFAULT now()", "DEFAULT (datetime('now'))")
            query = query.replace("SERIAL", "INTEGER")

            # Nếu insert mà không truyền id -> tự generate
            if "INSERT INTO" in query.upper() and "users" in query:
                if len(params) and "id" not in query.lower():
                    params = [str(uuid.uuid4())] + params

            if "INSERT INTO" in query.upper() and "refresh_tokens" in query:
                if len(params) and "id" not in query.lower():
                    params = [str(uuid.uuid4())] + params

        return query, params

    def execute(self, query: str, params=None):
        if params is None:
            params = []
        query, params = self.format_query(query, params)
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchall(self, query: str, params=None):
        if params is None:
            params = []
        query, params = self.format_query(query, params)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query: str, params=None):
        if params is None:
            params = []
        query, params = self.format_query(query, params)
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def new_tag(self, name: str):
        self.execute(
            "INSERT INTO tags (name) VALUES (%s);",
            (name.lower(),)
        )

        
def init_db(filename: str = "mydb", exists_ok: bool = True, reset: bool = False):
    """
    Initialize the database schema with both 'id' (auto-increment integer) 
    and 'uuid' (public unique identifier).

    Args:
        filename (str): Name of the SQLite database file (only applies in dev).
        exists_ok (bool): 
            - If True, tables will only be created if they do not already exist.
            - If False, existing tables will be dropped and recreated.
        reset (bool): 
            - If True, the entire database will be deleted and created again from scratch.
    """

    env = os.getenv("ENV", "dev")

    # If using SQLite and reset=True → delete the .sqlite3 file
    if reset and env == "dev":
        db_path = f"{filename}.sqlite3"
        if os.path.exists(db_path):
            os.remove(db_path)

    db = Database(filename=filename)

    if not exists_ok:
        db.execute("DROP TABLE IF EXISTS refresh_tokens;")
        db.execute("DROP TABLE IF EXISTS users;")

    if reset and env != "dev":
        # For Postgres, we cannot delete the database file,
        # so we simply drop the tables instead
        db.execute("DROP TABLE IF EXISTS refresh_tokens;")
        db.execute("DROP TABLE IF EXISTS users;")

    # Users table
    db.execute("""CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,                               -- Auto increment (INTEGER in SQLite)
        uuid UUID DEFAULT gen_random_uuid() UNIQUE,          -- Public UUID
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        pass TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMPTZ DEFAULT now());""")

    # Refresh tokens table
    db.execute("""CREATE TABLE IF NOT EXISTS refresh_tokens (
        id SERIAL PRIMARY KEY,
        uuid UUID DEFAULT gen_random_uuid() UNIQUE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash TEXT NOT NULL,
        revoked BOOLEAN DEFAULT FALSE,
        expires_at TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ DEFAULT now());""")

    # Document table
    db.execute("""CREATE TABLE documents (
        id SERIAL PRIMARY KEY,
        uuid UUID DEFAULT gen_random_uuid(),
        path TEXT NOT NULL,
        school TEXT DEFAULT 'HUS',
        faculty TEXT DEFAULT 'MIM',
        title TEXT NOT NULL,
        description TEXT,
        author TEXT,  -- upload user name
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        version INT DEFAULT 1,
        subject TEXT NOT NULL,
        course TEXT,  -- Có thể null
        document_type TEXT,  -- Ví dụ: Sách tham khảo
        keywords TEXT[],
        language TEXT DEFAULT 'Vietnamese',
        file_type TEXT,
        file_size INT,
        uploaded_by INT,  -- user.id
        access_level TEXT DEFAULT 'public',
        download_count INT DEFAULT 0);""")

    # tags tables
    db.execute("""CREATE TABLE tags (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL);""")

    # Document tag table
    db.execute("""CREATE TABLE document_tags (
        document_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        tag_id INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY(document_id, tag_id));""")

    db.close()
