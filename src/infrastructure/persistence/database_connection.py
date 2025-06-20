"""
Database connection abstraction for SQLite.

Provides connection management, schema initialization, and
transaction support for the infrastructure layer.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Union

from src.infrastructure.persistence.interfaces import IDatabaseConnection


class DatabaseConnection(IDatabaseConnection):
    """
    Manages SQLite database connections and schema initialization.

    Provides a clean abstraction over SQLite connections with proper
    configuration for the application's needs.
    """

    def __init__(self, database_path: Union[str, Path], timeout: float = 30.0):
        """
        Initialize database connection manager.

        Args:
            database_path: Path to SQLite database file
            timeout: Connection timeout in seconds
        """
        self.database_path = str(database_path)
        self.timeout = timeout
        self._connection: Optional[sqlite3.Connection] = None
        self._active_connections: List[sqlite3.Connection] = []

    def initialize_schema(self) -> None:
        """
        Initialize database schema with all required tables.

        Creates tables, indexes, and constraints if they don't exist.
        Safe to call multiple times (idempotent).
        """
        schema_sql = """
        -- Stock table
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            sector TEXT,
            industry_group TEXT,
            grade TEXT CHECK(grade IN ('A', 'B', 'C', NULL)),
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index on symbol for fast lookups
        CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock(symbol);
        
        -- Create trigger to update updated_at timestamp
        CREATE TRIGGER IF NOT EXISTS update_stock_timestamp 
        AFTER UPDATE ON stock
        BEGIN
            UPDATE stock SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        
        -- Portfolio table (placeholder for future implementation)
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            max_positions INTEGER NOT NULL,
            max_risk_per_trade REAL NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Stock transaction table (placeholder for future implementation)
        CREATE TABLE IF NOT EXISTS stock_transaction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            stock_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            transaction_date DATE NOT NULL,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
            FOREIGN KEY (stock_id) REFERENCES stock(id)
        );
        
        -- Target table (placeholder for future implementation)
        CREATE TABLE IF NOT EXISTS target (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER NOT NULL,
            portfolio_id INTEGER NOT NULL,
            pivot_price DECIMAL(10,2) NOT NULL,
            failure_price DECIMAL(10,2) NOT NULL,
            notes TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stock_id) REFERENCES stock(id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolio(id)
        );
        
        -- Portfolio balance table (placeholder for future implementation)
        CREATE TABLE IF NOT EXISTS portfolio_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            balance_date DATE NOT NULL,
            withdrawals DECIMAL(10,2) DEFAULT 0.00,
            deposits DECIMAL(10,2) DEFAULT 0.00,
            final_balance DECIMAL(10,2) NOT NULL,
            index_change DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
            UNIQUE(portfolio_id, balance_date)
        );
        
        -- Journal entry table (placeholder for future implementation)
        CREATE TABLE IF NOT EXISTS journal_entry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date DATE NOT NULL,
            content TEXT NOT NULL,
            stock_id INTEGER,
            portfolio_id INTEGER,
            transaction_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stock_id) REFERENCES stock(id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
            FOREIGN KEY (transaction_id) REFERENCES stock_transaction(id)
        );
        """

        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with proper configuration.

        Returns:
            Configured SQLite connection
        """
        connection = sqlite3.connect(
            self.database_path,
            timeout=self.timeout,
            check_same_thread=False,  # Allow connections across threads
        )

        # Configure connection
        connection.row_factory = sqlite3.Row  # Enable column access by name
        connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        connection.execute("PRAGMA journal_mode = WAL")  # Better concurrency

        # Track this connection
        self._active_connections.append(connection)

        return connection

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Automatically commits on success, rolls back on exception.
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def close(self) -> None:
        """
        Close all active database connections.

        Closes both the persistent connection (if any) and all tracked
        connections created by get_connection().
        """
        # Close persistent connection
        if self._connection:
            self._connection.close()
            self._connection = None

        # Close all tracked connections
        for conn in self._active_connections:
            try:
                conn.close()
            except sqlite3.ProgrammingError:
                # Connection already closed
                pass

        self._active_connections.clear()

    def __str__(self) -> str:
        """String representation of the database connection."""
        return f"DatabaseConnection(path='{self.database_path}')"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"DatabaseConnection(database_path='{self.database_path}', timeout={self.timeout})"
