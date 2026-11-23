import datetime
import logging
import os
import sqlite3
import threading
from dataclasses import asdict, fields
from typing import Any, Dict, List, Optional, Type, TypeVar

from dotenv import load_dotenv

from models import ChatMessage, Conversation, SavedFood, Scan, Subscription, User, Coupon, CouponRedemption, ReferralRecord, UserSyncBackup, FeedbackItem, ProductSubmission, ProductReport

load_dotenv()

logger = logging.getLogger("safebite.database")

Document = TypeVar("Document", User, Scan, SavedFood, Subscription, Conversation, ChatMessage, Coupon, CouponRedemption, ReferralRecord, UserSyncBackup, FeedbackItem, ProductSubmission, ProductReport)

# Safe fallback for PyMongo imports
try:
    from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument
    from pymongo.database import Database
    from pymongo.errors import (
        ConnectionFailure,
        DuplicateKeyError,
        PyMongoError,
        ServerSelectionTimeoutError,
    )
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False
    ASCENDING = 1
    DESCENDING = -1
    MongoClient = None
    Database = Any

    class DuplicateKeyError(Exception):
        pass

    class PyMongoError(Exception):
        pass

    class ServerSelectionTimeoutError(Exception):
        pass

    class ConnectionFailure(Exception):
        pass


MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "safebite").strip()
SQLITE_DB_PATH = os.path.abspath(
    os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "safebite.db"))
)


class MongoStore:
    """Typed persistence layer over the SafeBite MongoDB collections."""

    engine_name = "mongodb"

    _collection_names = {
        User: "users",
        Scan: "scans",
        SavedFood: "saved_foods",
        Subscription: "subscriptions",
        Coupon: "coupons",
        CouponRedemption: "coupon_redemptions",
        ReferralRecord: "referral_records",
        UserSyncBackup: "user_sync_backups",
        FeedbackItem: "feedback",
        ProductSubmission: "product_submissions",
        ProductReport: "product_reports",
    }

    def __init__(self, mongo_database: Any, mongo_client: Any = None):
        self.database = mongo_database
        self.client = mongo_client

    def _collection(self, document_type: Type[Document]):
        return self.database[self._collection_names[document_type]]

    def find_one(
        self, document_type: Type[Document], filters: dict[str, Any]
    ) -> Optional[Document]:
        document = self._collection(document_type).find_one(filters)
        return self._to_model(document_type, document) if document else None

    def find_many(
        self,
        document_type: Type[Document],
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[list[tuple[str, int]]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> list[Document]:
        cursor = self._collection(document_type).find(filters or {})
        if sort:
            cursor = cursor.sort(sort)
        if skip is not None:
            cursor = cursor.skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
        return [self._to_model(document_type, item) for item in cursor]

    def insert(self, document: Document) -> int:
        collection = self._collection(type(document))
        if document.id is None:
            counter = self.database["counters"].find_one_and_update(
                {"_id": collection.name},
                {"$inc": {"value": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
            document.id = counter["value"]

        collection.insert_one(asdict(document))
        return document.id

    def update(self, document: Document) -> None:
        if document.id is None:
            raise ValueError("Cannot update a MongoDB document without an id.")
        result = self._collection(type(document)).replace_one(
            {"id": document.id}, asdict(document)
        )
        if result.matched_count != 1:
            raise LookupError(
                f"{type(document).__name__} with id {document.id} no longer exists."
            )

    def delete(self, document: Document) -> bool:
        if document.id is None:
            return False
        result = self._collection(type(document)).delete_one({"id": document.id})
        return result.deleted_count == 1

    def delete_many(
        self, document_type: Type[Document], filters: dict[str, Any]
    ) -> int:
        return self._collection(document_type).delete_many(filters).deleted_count

    def count(
        self, document_type: Type[Document], filters: Optional[dict[str, Any]] = None
    ) -> int:
        return self._collection(document_type).count_documents(filters or {})

    def ping(self) -> bool:
        if self.database is not None:
            self.database.command("ping")
        return True

    def init(self) -> None:
        if self.database is None:
            return
        self.database["users"].create_index("id", unique=True)
        self.database["users"].create_index("username", unique=True)
        self.database["users"].create_index(
            "email",
            unique=True,
            partialFilterExpression={"email": {"$type": "string"}},
        )
        self.database["scans"].create_index("id", unique=True)
        self.database["scans"].create_index(
            [("user_id", ASCENDING), ("scan_date", DESCENDING)]
        )
        self.database["saved_foods"].create_index("id", unique=True)
        self.database["saved_foods"].create_index(
            [("user_id", ASCENDING), ("saved_date", DESCENDING)]
        )
        self.database["conversations"].create_index("id", unique=True)
        self.database["conversations"].create_index(
            [("user_id", ASCENDING), ("updated_at", DESCENDING)]
        )
        self.database["chat_messages"].create_index("id", unique=True)
        self.database["chat_messages"].create_index(
            [("conversation_id", ASCENDING), ("created_at", ASCENDING)]
        )
        self.database["coupons"].create_index("id", unique=True)
        self.database["coupons"].create_index("code", unique=True)
        self.database["coupon_redemptions"].create_index("id", unique=True)
        self.database["coupon_redemptions"].create_index("user_id", unique=True)
        for collection_name in ("users", "scans", "saved_foods", "conversations", "chat_messages", "coupons", "coupon_redemptions"):
            self.database["counters"].update_one(
                {"_id": collection_name},
                {"$setOnInsert": {"value": 0}},
                upsert=True,
            )

    def close(self) -> None:
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass

    @staticmethod
    def _to_model(document_type: Type[Document], document: dict[str, Any]) -> Document:
        document.pop("_id", None)
        return document_type(**document)


class SQLiteStore(MongoStore):
    """Thread-safe SQLite storage providing the exact same typed interface as MongoStore."""

    engine_name = "sqlite"

    _table_names = {
        User: "users",
        Scan: "scans",
        SavedFood: "saved_foods",
        Subscription: "subscriptions",
        Conversation: "conversations",
        ChatMessage: "chat_messages",
        Coupon: "coupons",
        CouponRedemption: "coupon_redemptions",
        ReferralRecord: "referral_records",
        UserSyncBackup: "user_sync_backups",
        FeedbackItem: "feedback",
        ProductSubmission: "product_submissions",
        ProductReport: "product_reports",
    }

    _date_fields = {
        User: {"verification_expires_at", "verification_last_sent_at", "created_at"},
        Scan: {"scan_date"},
        SavedFood: {"saved_date"},
        Subscription: {"start_time", "expiry_time", "verified_at", "last_checked_at"},
        Conversation: {"created_at", "updated_at"},
        ChatMessage: {"created_at"},
        Coupon: {"expires_at", "created_at"},
        CouponRedemption: {"redeemed_at", "premium_until"},
    }

    _bool_fields = {
        User: {"is_diabetic", "is_verified", "email_verified"},
        Scan: set(),
        SavedFood: set(),
        Subscription: {"auto_renewing"},
        Conversation: set(),
        ChatMessage: set(),
        Coupon: {"active"},
        CouponRedemption: set(),
    }

    _int_fields = {
        User: {"age", "failed_verification_attempts"},
        Scan: set(),
        SavedFood: set(),
        Subscription: set(),
        Conversation: set(),
        ChatMessage: set(),
        Coupon: {"days_free", "max_redemptions", "redeemed_count"},
        CouponRedemption: set(),
    }

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        self.database = None
        self.client = None

    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                conn.execute("PRAGMA journal_mode=WAL")
            except Exception:
                pass
            self._local.conn = conn
        return self._local.conn

    def ping(self) -> bool:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return cursor.fetchone() is not None

    def init(self) -> None:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                age INTEGER,
                height REAL,
                weight REAL,
                gender TEXT,
                is_diabetic INTEGER DEFAULT 0,
                dietary_preference TEXT DEFAULT 'None',
                allergens TEXT DEFAULT '',
                ingredient_exclusions TEXT DEFAULT '',
                email TEXT UNIQUE,
                is_verified INTEGER DEFAULT 0,
                email_verified INTEGER DEFAULT 0,
                verification_code_hash TEXT,
                verification_expires_at TEXT,
                verification_last_sent_at TEXT,
                failed_verification_attempts INTEGER DEFAULT 0,
                created_at TEXT
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_name TEXT DEFAULT 'Food Product',
                calories REAL,
                protein REAL,
                carbs REAL,
                fat REAL,
                sugar REAL,
                fiber REAL,
                sodium REAL,
                saturated_fat REAL,
                trans_fat REAL,
                ingredients TEXT,
                health_score REAL DEFAULT 70.0,
                classification TEXT DEFAULT 'Moderate',
                analysis TEXT,
                healthier_alternatives TEXT,
                benefits TEXT,
                concerns TEXT,
                image_path TEXT,
                scan_date TEXT
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_name TEXT DEFAULT 'Saved Food',
                calories REAL,
                protein REAL,
                carbs REAL,
                fat REAL,
                sugar REAL,
                fiber REAL,
                sodium REAL,
                ingredients TEXT,
                health_score REAL,
                analysis TEXT,
                image_path TEXT,
                saved_date TEXT
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                purchase_token_hash TEXT UNIQUE NOT NULL,
                order_id TEXT,
                status TEXT NOT NULL,
                start_time TEXT,
                expiry_time TEXT,
                auto_renewing INTEGER DEFAULT 1,
                verified_at TEXT,
                last_checked_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                scan_context TEXT,
                created_at TEXT,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS ix_conversations_user_updated ON conversations(user_id, updated_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS ix_chat_messages_conv_created ON chat_messages(conversation_id, created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS ix_users_username ON users(username)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS ix_scans_user_date ON scans(user_id, scan_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS ix_saved_user_date ON saved_foods(user_id, saved_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS ix_subs_user_id ON subscriptions(user_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS ix_subs_token_hash ON subscriptions(purchase_token_hash)"
            )
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                days_free INTEGER DEFAULT 30,
                max_redemptions INTEGER,
                expires_at TEXT,
                active INTEGER DEFAULT 1,
                redeemed_count INTEGER DEFAULT 0,
                created_at TEXT
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupon_redemptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                code TEXT NOT NULL,
                redeemed_at TEXT,
                premium_until TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_coupons_code ON coupons(code)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_redemptions_user_id ON coupon_redemptions(user_id)")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS referral_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_user_id INTEGER NOT NULL,
                referee_user_id INTEGER NOT NULL,
                referral_code TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY(referrer_user_id) REFERENCES users(id),
                FOREIGN KEY(referee_user_id) REFERENCES users(id)
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sync_backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                history_json TEXT,
                saved_foods_json TEXT,
                profiles_json TEXT,
                settings_json TEXT,
                device_id TEXT,
                updated_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                feedback_type TEXT DEFAULT 'general',
                message TEXT NOT NULL,
                rating INTEGER,
                screenshot_path TEXT,
                app_version TEXT,
                os_version TEXT,
                device_model TEXT,
                created_at TEXT
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                product_name TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                serving_size TEXT,
                calories REAL,
                protein REAL,
                carbohydrates REAL,
                total_sugar REAL,
                total_fat REAL,
                saturated_fat REAL,
                sodium REAL,
                fiber REAL,
                ingredients TEXT,
                submitted_by_user_id INTEGER,
                submission_count INTEGER DEFAULT 1,
                is_approved INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                user_id INTEGER,
                reason TEXT NOT NULL,
                details TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_referrals_referrer ON referral_records(referrer_user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_referrals_referee ON referral_records(referee_user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_referrals_code ON referral_records(referral_code)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_sync_user_id ON user_sync_backups(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_submissions_barcode ON product_submissions(barcode)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_reports_barcode ON product_reports(barcode)")

            # Migration guard: Drop legacy phone OTP columns if present
            try:
                res = cursor.execute("PRAGMA table_info(users)")
                existing_cols = {row["name"] for row in res.fetchall()}
                phone_cols = [
                    "phone_number",
                    "phone_verified",
                    "phone_verification_code_hash",
                    "phone_verification_expires_at",
                    "phone_verification_last_sent_at",
                    "failed_phone_attempts"
                ]
                for pcol in phone_cols:
                    if pcol in existing_cols:
                        cursor.execute(f"ALTER TABLE users DROP COLUMN {pcol}")
            except Exception as dme:
                logger.debug("SQLite drop column: %s", dme)

            # Migration guard: Add missing columns if upgrading from legacy SQLite
            try:
                res = cursor.execute("PRAGMA table_info(users)")
                existing_cols = {row["name"] for row in res.fetchall()}
                user_flds = {f.name: f.type for f in fields(User)}
                for col_name in user_flds:
                    if col_name not in existing_cols and col_name != "id":
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} TEXT")
            except Exception as me:
                logger.debug("SQLite column check: %s", me)

            conn.commit()

    def _build_where(self, filters: Optional[dict[str, Any]]) -> tuple[str, list[Any]]:
        if not filters:
            return "", []
        clauses = []
        params = []
        for key, value in filters.items():
            if key == "$or" and isinstance(value, list):
                or_parts = []
                for item in value:
                    sub_parts = []
                    for sub_k, sub_v in item.items():
                        sub_parts.append(f"{sub_k} = ?")
                        params.append(sub_v)
                    if sub_parts:
                        or_parts.append(" AND ".join(sub_parts))
                if or_parts:
                    clauses.append(f"({' OR '.join(or_parts)})")
            elif key.startswith("$"):
                continue
            else:
                clauses.append(f"{key} = ?")
                params.append(value)
        if not clauses:
            return "", []
        return " WHERE " + " AND ".join(clauses), params

    def _row_to_model(
        self, document_type: Type[Document], row: sqlite3.Row
    ) -> Document:
        data = dict(row)
        bool_fields = self._bool_fields.get(document_type, set())
        date_fields = self._date_fields.get(document_type, set())
        int_fields = self._int_fields.get(document_type, set())

        for bf in bool_fields:
            if bf in data and data[bf] is not None:
                data[bf] = bool(data[bf])

        for inf in int_fields:
            if inf in data and data[inf] is not None:
                try:
                    data[inf] = int(data[inf])
                except Exception:
                    pass

        for df in date_fields:
            if df in data and data[df] is not None:
                if isinstance(data[df], str):
                    try:
                        data[df] = datetime.datetime.fromisoformat(data[df])
                    except Exception:
                        pass

        valid_field_names = {f.name for f in fields(document_type)}
        cleaned = {k: v for k, v in data.items() if k in valid_field_names}
        return document_type(**cleaned)

    def find_one(
        self, document_type: Type[Document], filters: dict[str, Any]
    ) -> Optional[Document]:
        table = self._table_names[document_type]
        where_clause, params = self._build_where(filters)
        sql = f"SELECT * FROM {table}{where_clause} LIMIT 1"
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return self._row_to_model(document_type, row) if row else None

    def find_many(
        self,
        document_type: Type[Document],
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[list[tuple[str, int]]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> list[Document]:
        table = self._table_names[document_type]
        where_clause, params = self._build_where(filters)
        order_clause = ""
        if sort:
            sort_parts = []
            for col, direction in sort:
                dir_str = "DESC" if direction == -1 else "ASC"
                sort_parts.append(f"{col} {dir_str}")
            if sort_parts:
                order_clause = " ORDER BY " + ", ".join(sort_parts)
        limit_clause = ""
        if limit is not None:
            limit_clause = f" LIMIT {int(limit)}"
            if skip is not None:
                limit_clause += f" OFFSET {int(skip)}"
        elif skip is not None:
            limit_clause = f" LIMIT -1 OFFSET {int(skip)}"
        sql = f"SELECT * FROM {table}{where_clause}{order_clause}{limit_clause}"
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_model(document_type, row) for row in rows]

    def insert(self, document: Document) -> int:
        table = self._table_names[type(document)]
        raw_data = asdict(document)
        for k, v in list(raw_data.items()):
            if isinstance(v, bool):
                raw_data[k] = 1 if v else 0
            elif isinstance(v, (datetime.datetime, datetime.date)):
                raw_data[k] = v.isoformat()

        if document.id is None:
            raw_data.pop("id", None)

        cols = list(raw_data.keys())
        placeholders = ["?"] * len(cols)
        vals = [raw_data[c] for c in cols]
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(sql, vals)
                conn.commit()
                document.id = cursor.lastrowid
                return document.id
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise DuplicateKeyError(
                    f"A record with this value already exists: {e}"
                )

    def update(self, document: Document) -> None:
        if document.id is None:
            raise ValueError("Cannot update a document without an id.")
        table = self._table_names[type(document)]
        raw_data = asdict(document)
        doc_id = raw_data.pop("id")
        for k, v in list(raw_data.items()):
            if isinstance(v, bool):
                raw_data[k] = 1 if v else 0
            elif isinstance(v, (datetime.datetime, datetime.date)):
                raw_data[k] = v.isoformat()

        cols = list(raw_data.keys())
        set_clause = ", ".join(f"{col} = ?" for col in cols)
        vals = [raw_data[c] for c in cols] + [doc_id]
        sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(sql, vals)
                conn.commit()
                if cursor.rowcount < 1:
                    raise LookupError(
                        f"{type(document).__name__} with id {doc_id} no longer exists."
                    )
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise DuplicateKeyError(
                    f"Duplicate value error during update: {e}"
                )

    def delete(self, document: Document) -> bool:
        if document.id is None:
            return False
        table = self._table_names[type(document)]
        sql = f"DELETE FROM {table} WHERE id = ?"
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, [document.id])
            conn.commit()
            return cursor.rowcount == 1

    def delete_many(
        self, document_type: Type[Document], filters: dict[str, Any]
    ) -> int:
        table = self._table_names[document_type]
        where_clause, params = self._build_where(filters)
        sql = f"DELETE FROM {table}{where_clause}"
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount

    def count(
        self,
        document_type: Type[Document],
        filters: Optional[dict[str, Any]] = None,
    ) -> int:
        table = self._table_names[document_type]
        where_clause, params = self._build_where(filters)
        sql = f"SELECT COUNT(*) FROM {table}{where_clause}"
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return int(row[0]) if row else 0

    def close(self) -> None:
        with self._lock:
            if hasattr(self._local, "conn") and self._local.conn is not None:
                try:
                    self._local.conn.close()
                except Exception:
                    pass
                self._local.conn = None


def create_store() -> MongoStore:
    """Creates the persistence store.
    Tries MongoDB if MONGODB_URI is configured with a reachable server;
    otherwise gracefully falls back to SQLite to guarantee zero downtime on Render.
    """
    is_prod = bool(os.getenv("RENDER") or os.getenv("PORT"))

    if MONGODB_URI and HAS_PYMONGO:
        # Avoid connecting to 127.0.0.1 on Render where no local daemon runs
        if is_prod and ("127.0.0.1" in MONGODB_URI or "localhost" in MONGODB_URI):
            logger.warning(
                "Render deployment detected with local MongoDB URI (%s). "
                "Local MongoDB is not available inside Render containers. "
                "Seamlessly falling back to SQLite storage.",
                MONGODB_URI,
            )
            return SQLiteStore(SQLITE_DB_PATH)

        try:
            logger.info("Connecting to MongoDB at %s...", MONGODB_URI.split("@")[-1] if "@" in MONGODB_URI else "specified host")
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            database = client[MONGODB_DATABASE or "safebite"]
            logger.info("MongoDB connected successfully. Active database: %s", database.name)
            return MongoStore(database, mongo_client=client)
        except Exception as exc:
            logger.warning(
                "MongoDB connection could not be established (%s). "
                "Seamlessly falling back to SQLite database at %s.",
                exc,
                SQLITE_DB_PATH,
            )
            return SQLiteStore(SQLITE_DB_PATH)

    logger.info("No remote MONGODB_URI configured. Running with SQLite database at %s.", SQLITE_DB_PATH)
    return SQLiteStore(SQLITE_DB_PATH)


store: MongoStore = create_store()
try:
    store.init()
except Exception as _e:
    logger.debug("Database initial auto-migration: %s", _e)
database = getattr(store, "database", None)
client = getattr(store, "client", None)


def get_db():
    yield store


def seed_default_coupons(persistence_store) -> None:
    """Seeds default promo coupons (NEMI100, GUDDU100) if not present."""
    try:
        now = datetime.datetime.utcnow()
        for c_code in ("NEMI100", "GUDDU100"):
            existing = persistence_store.find_one(Coupon, {"code": c_code})
            if not existing:
                persistence_store.insert(Coupon(
                    code=c_code,
                    days_free=30,
                    max_redemptions=None,
                    expires_at=None,
                    active=True,
                    redeemed_count=0,
                    created_at=now
                ))
                logger.info("Seeded coupon: %s (30 days free)", c_code)
    except Exception as exc:
        logger.warning("Coupon seed warning: %s", exc)


def init_db() -> None:
    """Initializes schema, indexes, and tables for the active database engine."""
    try:
        store.init()
        seed_default_coupons(store)
        store.ping()
        logger.info("SafeBite database engine '%s' initialized and verified.", store.engine_name)
    except Exception as exc:
        logger.warning("Database init warning: %s", exc)


def close_db() -> None:
    store.close()
