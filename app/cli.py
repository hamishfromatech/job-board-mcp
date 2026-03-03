"""CLI commands for job board management."""

import argparse
import sys

from app.database import init_db, seed_database
from app.database import SessionLocal


def init_database():
    """Initialize the database with tables and seed data."""
    print("Creating database tables...")
    init_db()

    print("Seeding database with sample data...")
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    print("Database initialized successfully!")


def reset_database():
    """Reset the database (WARNING: deletes all data)."""
    confirm = input("This will DELETE all data. Type 'yes' to confirm: ")
    if confirm != "yes":
        print("Cancelled.")
        return

    from app.database import Base, engine

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Recreating tables...")
    init_db()

    print("Seeding database...")
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    print("Database reset complete!")


def seed_only():
    """Only seed data without creating tables."""
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Job Board MCP CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init_db command
    init_parser = subparsers.add_parser("init_db", help="Initialize database with tables and seed data")

    # reset_db command
    reset_parser = subparsers.add_parser("reset_db", help="Reset database (WARNING: deletes all data)")

    # seed command
    seed_parser = subparsers.add_parser("seed", help="Seed database with sample data")

    args = parser.parse_args()

    if args.command == "init_db":
        init_database()
    elif args.command == "reset_db":
        reset_database()
    elif args.command == "seed":
        seed_only()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
