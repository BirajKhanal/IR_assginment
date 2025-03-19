import psycopg2
from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL, DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


def create_database_if_not_exists():
    """
    Connects to PostgreSQL default database (postgres) and creates the target database if it does not exist.
    """
    try:
        # Connect to default 'postgres' database
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{DB_NAME}' does not exist. Creating it now...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully!")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")


# Ensure the database exists before initializing SQLAlchemy/SQLModel
create_database_if_not_exists()

# Create SQLModel engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """
    Creates all tables defined in SQLModel.
    """
    SQLModel.metadata.create_all(engine)


def get_db():
    """
    Dependency for getting a database session.
    """
    with Session(engine) as session:
        yield session
