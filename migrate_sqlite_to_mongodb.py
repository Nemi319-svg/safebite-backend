"""Import existing SafeBite SQLite records into the configured MongoDB database."""

import argparse
import datetime
import sqlite3
from pathlib import Path

from database import database, init_db

DATETIME_COLUMNS = {
    "users": (
        "created_at",
        "verification_expires_at",
        "verification_last_sent_at",
    ),
    "scans": ("scan_date",),
    "saved_foods": ("saved_date",),
}


def parse_datetime(value):
    if not value or isinstance(value, datetime.datetime):
        return value
    return datetime.datetime.fromisoformat(value)


def migrate_table(connection, table: str, dry_run: bool) -> int:
    rows = connection.execute(f'SELECT * FROM "{table}"').fetchall()
    documents = []
    for row in rows:
        document = dict(row)
        for column in DATETIME_COLUMNS[table]:
            if column in document:
                document[column] = parse_datetime(document[column])
        documents.append(document)

    collection = database[table]
    if not dry_run:
        for document in documents:
            collection.replace_one({"id": document["id"]}, document, upsert=True)
        if documents:
            database["counters"].update_one(
                {"_id": table},
                {"$max": {"value": max(document["id"] for document in documents)}},
                upsert=True,
            )
    return len(documents)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sqlite-path",
        default=str(Path(__file__).resolve().parent / "safebite.db"),
        help="Path to the existing SQLite database (default: backend/safebite.db).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count source rows without writing to MongoDB.",
    )
    args = parser.parse_args()

    sqlite_path = Path(args.sqlite_path).expanduser().resolve()
    if not sqlite_path.is_file():
        parser.error(f"SQLite database does not exist: {sqlite_path}")

    connection = sqlite3.connect(sqlite_path)
    connection.row_factory = sqlite3.Row
    try:
        init_db()
        for table in ("users", "scans", "saved_foods"):
            count = migrate_table(connection, table, args.dry_run)
            action = "Found" if args.dry_run else "Imported"
            print(f"{action} {count} {table} records.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
