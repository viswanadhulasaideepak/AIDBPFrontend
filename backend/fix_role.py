from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./employees.db")

with engine.begin() as conn:

    # Rename old table
    conn.execute(text("""
        ALTER TABLE holidays RENAME TO holidays_old;
    """))

    # Create new holidays table
    conn.execute(text("""
        CREATE TABLE holidays (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            created_by VARCHAR NOT NULL DEFAULT 'admin',
            holiday_date DATETIME NOT NULL,
            description TEXT,
            holiday_type VARCHAR(20) NOT NULL,
            recurring BOOLEAN DEFAULT 0,
            company_id INTEGER NOT NULL,
            created_at DATETIME
        );
    """))

    # Copy old data into new table
    conn.execute(text("""
        INSERT INTO holidays (
            id,
            name,
            created_by,
            holiday_date,
            description,
            holiday_type,
            recurring,
            company_id,
            created_at
        )
        SELECT
            id,
            name,
            'admin',
            date,
            description,
            holiday_type,
            recurring,
            company_id,
            created_at
        FROM holidays_old;
    """))

    # Remove old table
    conn.execute(text("""
        DROP TABLE holidays_old;
    """))

print("Holiday table migrated successfully.")