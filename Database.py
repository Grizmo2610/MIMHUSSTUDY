import os
import sqlite3
import psycopg2
import uuid
import bcrypt
from datetime import datetime
from utils.query import split_search_text

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

            query = query.replace("UUID", "TEXT")
            query = query.replace("TIMESTAMPTZ", "TEXT")
            query = query.replace("DEFAULT gen_random_uuid()", "")
            query = query.replace("DEFAULT now()", "DEFAULT (datetime('now'))")
            query = query.replace("SERIAL", "INTEGER")

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
        """Thêm tag mới nếu chưa tồn tại"""
        name = str(name).strip().lower()
        exists = self.fetchone("SELECT id FROM tags WHERE name = %s;", (name, ))
        if not exists:
            self.execute("INSERT INTO tags (name) VALUES (%s);", [name])
            return True
        return False

    def new_user(self, name: str, email: str, password: str, role="user"):
        """Thêm user mới nếu email chưa tồn tại"""
        email = email.strip().lower()
        exists = self.fetchone("SELECT id FROM users WHERE email = %s;", (email, ))
        if exists:
            return False

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.execute(
            "INSERT INTO users (uuid, email, name, pass, role) VALUES (%s, %s, %s, %s, %s);",
            [str(uuid.uuid4()), email, name, hashed_password, role]
        )
        return True

    def new_document(self, path: str, title: str, subject: str,
                     author: str = None,
                     description: str = None,
                     course: str = None,
                     school: str = "HUS",
                     faculty: str = "MIM",
                     language: str = "Vietnamese",
                     uploaded_by: int = None,
                     access_level: str = "public",
                     version: int = 1):
        """
        Thêm document mới vào DB.
        file_type và file_size tự lấy từ path.
        Các tham số có default thì có thể không truyền.
        """
        # Lấy file_type và file_size từ path
        file_type = os.path.splitext(path)[1][1:] if path else "Plain"  # bỏ dấu .
        file_size = os.path.getsize(path) if path and os.path.exists(path) else 0

        # Chèn document
        self.execute(
            """INSERT INTO documents
               (uuid, path, school, faculty, title, description, author, created_at,
                last_updated, version, subject, course, language, file_type, file_size,
                uploaded_by, access_level)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
            [
                str(uuid.uuid4()), path, school, faculty, title, description, author,
                datetime.now(), datetime.now(), version, subject, course, language,
                file_type, file_size, uploaded_by, access_level
            ]
        )

        # Lấy id document vừa thêm
        doc_id = self.fetchone("SELECT id FROM documents WHERE path = %s;", [path, ])
        return doc_id

    def add_tag_to_document(self, document_id: int, tag_name: str):
        """Gán tag cho document"""
        # Lấy tag id, nếu chưa tồn tại thì tạo mới
        tag_name = tag_name.strip().lower()
        
        tag = self.fetchone("SELECT id FROM tags WHERE name = %s;", [tag_name, ])
        if not tag:
            self.new_tag(tag_name)
            tag = self.fetchone("SELECT id FROM tags WHERE name = %s;", (tag_name, ))

        tag_id = tag[0]

        exists = self.fetchone(
            "SELECT * FROM document_tags WHERE document_id = %s AND tag_id = %s;",
            (document_id, tag_id)
        )
        if not exists:
            self.execute(
                "INSERT INTO document_tags (document_id, tag_id) VALUES (%s, %s);",
                [document_id, tag_id]
            )
            return True
        return False
    
    def search_documents(self, text: str = None, filters: dict = None):
        """
        Search documents like Google Search:
        - text: input của người dùng, có thể có cụm "..." giữ nguyên
        - filters: dict các trường filter exact match, ví dụ {"school": "HUS"}
        """
        query = "SELECT * FROM documents WHERE 1=1"
        params = []

        columns = ["title", "description", "author", "subject", "school"]
        weights = [5, 2, 3, 4, 1]  # trọng số cột, có thể điều chỉnh

        # 1. Tokenize input text
        if text:
            tokens = split_search_text(text)
            if tokens:
                token_clauses = []
                score_clauses = []

                for token in tokens:
                    # OR giữa cột, AND giữa token
                    col_clauses = [f"{col} LIKE %s" for col in columns]
                    token_clauses.append("(" + " OR ".join(col_clauses) + ")")
                    
                    # Tính score
                    score_clauses.extend([f"CASE WHEN {col} LIKE %s THEN {w} ELSE 0 END"
                                        for col, w in zip(columns, weights)])
                    
                    # params cho token search
                    params.extend([f"%{token}%" for _ in columns])  # cho WHERE
                    params.extend([f"%{token}%" for _ in columns])  # cho score

                # AND giữa các token
                query += " AND " + " AND ".join(token_clauses)

        # 2. Filter từ dict
        if filters:
            for field, value in filters.items():
                query += f" AND {field} = %s"
                params.append(value)

        # 3. Tạo query có ranking score
        if text:
            score_expr = " + ".join(score_clauses)
            query = f"SELECT *, ({score_expr}) AS score FROM documents WHERE 1=1" + query[len("SELECT * FROM documents WHERE 1=1"):]
            query += " ORDER BY score DESC"

        # 4. Execute
        return self.fetchall(query, params)


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
