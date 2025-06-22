"""
Database connection abstraction for SQLite.

Provides connection management, schema initialization, and
transaction support for the infrastructure layer.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Optional, Union

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
            id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            sector TEXT,
            industry_group TEXT,
            grade TEXT CHECK(grade IN ('A', 'B', 'C', NULL)),
            notes TEXT,
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
        
        -- Portfolio table
        CREATE TABLE IF NOT EXISTS portfolio (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            max_positions INTEGER DEFAULT 10,
            max_risk_per_trade DECIMAL(3,1) DEFAULT 2.0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create trigger to update portfolio timestamp
        CREATE TRIGGER IF NOT EXISTS update_portfolio_timestamp
        AFTER UPDATE ON portfolio
        BEGIN
            UPDATE portfolio SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        
        -- Stock transaction table
        CREATE TABLE IF NOT EXISTS stock_transaction (
            id TEXT PRIMARY KEY,
            portfolio_id TEXT NOT NULL,
            stock_id TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('buy', 'sell')),
            quantity INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            transaction_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
            FOREIGN KEY (stock_id) REFERENCES stock(id)
        );
        
        -- Target table
        CREATE TABLE IF NOT EXISTS target (
            id TEXT PRIMARY KEY,
            stock_id TEXT NOT NULL,
            portfolio_id TEXT NOT NULL,
            pivot_price DECIMAL(10,2) NOT NULL,
            failure_price DECIMAL(10,2) NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'hit', 'failed', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stock_id) REFERENCES stock(id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolio(id)
        );
        
        -- Create trigger to update target timestamp
        CREATE TRIGGER IF NOT EXISTS update_target_timestamp
        AFTER UPDATE ON target
        BEGIN
            UPDATE target SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        
        -- Portfolio balance table
        CREATE TABLE IF NOT EXISTS portfolio_balance (
            id TEXT PRIMARY KEY,
            portfolio_id TEXT NOT NULL,
            balance_date DATE NOT NULL,
            withdrawals DECIMAL(12,2) DEFAULT 0,
            deposits DECIMAL(12,2) DEFAULT 0,
            final_balance DECIMAL(12,2) NOT NULL,
            index_change DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
            UNIQUE(portfolio_id, balance_date)
        );
        
        -- Journal entry table
        CREATE TABLE IF NOT EXISTS journal_entry (
            id TEXT PRIMARY KEY,
            entry_date DATE NOT NULL,
            content TEXT NOT NULL,
            stock_id TEXT,
            portfolio_id TEXT,
            transaction_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stock_id) REFERENCES stock(id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
            FOREIGN KEY (transaction_id) REFERENCES stock_transaction(id)
        );
        
        -- Create trigger to update journal entry timestamp
        CREATE TRIGGER IF NOT EXISTS update_journal_entry_timestamp
        AFTER UPDATE ON journal_entry
        BEGIN
            UPDATE journal_entry SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_transaction_portfolio ON stock_transaction(portfolio_id);
        CREATE INDEX IF NOT EXISTS idx_transaction_stock ON stock_transaction(stock_id);
        CREATE INDEX IF NOT EXISTS idx_transaction_date ON stock_transaction(transaction_date);
        CREATE INDEX IF NOT EXISTS idx_target_status ON target(status);
        CREATE INDEX IF NOT EXISTS idx_portfolio_balance_date ON portfolio_balance(balance_date);
        CREATE INDEX IF NOT EXISTS idx_journal_entry_date ON journal_entry(entry_date);
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
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
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
