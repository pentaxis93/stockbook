"""
Database utilities for StockBook
Handles all database operations including initialization, CRUD operations, and queries
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = Path("database/stockbook.db")
SCHEMA_PATH = Path("database/schema.sql")


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database with schema."""
    # Create database directory if it doesn't exist
    DB_PATH.parent.mkdir(exist_ok=True)

    # Read schema file
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()

    # Execute the schema to create all tables, indexes, and triggers
    with get_db_connection() as conn:
        conn.executescript(schema)
        conn.commit()

    logger.info("Database initialized successfully")


def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert sqlite3.Row to dictionary."""
    return dict(zip(row.keys(), row))


# Stock operations
class StockDB:
    @staticmethod
    def create(symbol: str, name: str, industry_group: Optional[str] = None,
               grade: Optional[str] = None, notes: Optional[str] = None) -> int:
        """Create a new stock record."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO stock (symbol, name, industry_group, grade, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (symbol, name, industry_group, grade, notes)
            )
            conn.commit()
            stock_id = cursor.lastrowid
            if stock_id is None:
                raise RuntimeError("Failed to create stock")
            return stock_id

    @staticmethod
    def get_by_symbol(symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock by symbol."""
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT * FROM stock WHERE symbol = ?", (symbol,)
            ).fetchone()
            return dict_from_row(row) if row else None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all stocks."""
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM stock ORDER BY symbol").fetchall()
            return [dict_from_row(row) for row in rows]

    @staticmethod
    def update(stock_id: int, **kwargs) -> bool:
        """Update stock fields."""
        allowed_fields = ['name', 'industry_group', 'grade', 'notes']
        fields_to_update = {k: v for k,
                            v in kwargs.items() if k in allowed_fields}

        if not fields_to_update:
            return False

        set_clause = ", ".join([f"{k} = ?" for k in fields_to_update.keys()])
        values = list(fields_to_update.values()) + [stock_id]

        with get_db_connection() as conn:
            conn.execute(
                f"UPDATE stock SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()
            return True


# Portfolio operations
class PortfolioDB:
    @staticmethod
    def create(name: str, max_positions: int = 10,
               max_risk_per_trade: float = 2.0) -> int:
        """Create a new portfolio."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO portfolio (name, max_positions, max_risk_per_trade)
                   VALUES (?, ?, ?)""",
                (name, max_positions, max_risk_per_trade)
            )
            conn.commit()
            portfolio_id = cursor.lastrowid
            if portfolio_id is None:
                raise RuntimeError("Failed to create portfolio")
            return portfolio_id

    @staticmethod
    def get_all_active() -> List[Dict[str, Any]]:
        """Get all active portfolios."""
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM portfolio WHERE is_active = TRUE ORDER BY name"
            ).fetchall()
            return [dict_from_row(row) for row in rows]

    @staticmethod
    def get_by_id(portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Get portfolio by ID."""
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT * FROM portfolio WHERE id = ?", (portfolio_id,)
            ).fetchone()
            return dict_from_row(row) if row else None


# Transaction operations
class StockTransactionDB:
    @staticmethod
    def create(portfolio_id: int, stock_id: int, transaction_type: str,
               quantity: int, price: float, transaction_date: date,
               notes: Optional[str] = None) -> int:
        """Create a new transaction."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO stock_transaction (portfolio_id, stock_id, type,
                   quantity, price, transaction_date, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (portfolio_id, stock_id, transaction_type, quantity, price,
                 transaction_date, notes)
            )
            conn.commit()
            transaction_id = cursor.lastrowid
            if transaction_id is None:
                raise RuntimeError("Failed to create transaction")
            return transaction_id

    @staticmethod
    def get_portfolio_transactions(portfolio_id: int) -> List[Dict[str, Any]]:
        """Get all transactions for a portfolio."""
        with get_db_connection() as conn:
            rows = conn.execute(
                """SELECT t.*, s.symbol, s.name as stock_name
                   FROM stock_transaction t
                   JOIN stock s ON t.stock_id = s.id
                   WHERE t.portfolio_id = ?
                   ORDER BY t.transaction_date DESC""",
                (portfolio_id,)
            ).fetchall()
            return [dict_from_row(row) for row in rows]

    @staticmethod
    def get_holdings(portfolio_id: int) -> List[Dict[str, Any]]:
        """Get current holdings for a portfolio."""
        with get_db_connection() as conn:
            rows = conn.execute(
                """SELECT
                    s.id as stock_id,
                    s.symbol,
                    s.name,
                    s.grade,
                    SUM(CASE WHEN t.type = 'buy' THEN t.quantity
                             WHEN t.type = 'sell' THEN -t.quantity END) as shares,
                    SUM(CASE WHEN t.type = 'buy' THEN t.quantity * t.price
                             WHEN t.type = 'sell' THEN -(t.quantity * t.price) END) as cost_basis
                   FROM stock_transaction t
                   JOIN stock s ON t.stock_id = s.id
                   WHERE t.portfolio_id = ?
                   GROUP BY s.id
                   HAVING shares > 0""",
                (portfolio_id,)
            ).fetchall()
            return [dict_from_row(row) for row in rows]


# Target operations
class TargetDB:
    @staticmethod
    def create(stock_id: int, portfolio_id: int, pivot_price: float,
               failure_price: float, notes: Optional[str] = None) -> int:
        """Create a new stock target."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO target (stock_id, portfolio_id,
                   pivot_price, failure_price, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (stock_id, portfolio_id, pivot_price, failure_price, notes)
            )
            conn.commit()
            target_id = cursor.lastrowid
            if target_id is None:
                raise RuntimeError("Failed to create target")
            return target_id

    @staticmethod
    def get_active_targets(portfolio_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get active targets, optionally filtered by portfolio."""
        query = """SELECT t.*, s.symbol, s.name as stock_name, p.name as portfolio_name
                   FROM target t
                   JOIN stock s ON t.stock_id = s.id
                   JOIN portfolio p ON t.portfolio_id = p.id
                   WHERE t.status = 'active'"""

        params = []
        if portfolio_id:
            query += " AND t.portfolio_id = ?"
            params.append(portfolio_id)

        query += " ORDER BY s.symbol"

        with get_db_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict_from_row(row) for row in rows]

    @staticmethod
    def update_status(target_id: int, status: str) -> bool:
        """Update target status."""
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE target SET status = ? WHERE id = ?",
                (status, target_id)
            )
            conn.commit()
            return True


# Portfolio Balance operations
class PortfolioBalanceDB:
    @staticmethod
    def create(portfolio_id: int, balance_date: date, final_balance: float,
               withdrawals: float = 0, deposits: float = 0,
               index_change: Optional[float] = None) -> int:
        """Create or update portfolio balance for a date."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """INSERT OR REPLACE INTO portfolio_balance
                   (portfolio_id, balance_date, withdrawals, deposits,
                    final_balance, index_change)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (portfolio_id, balance_date, withdrawals, deposits,
                 final_balance, index_change)
            )
            conn.commit()
            balance_id = cursor.lastrowid
            if balance_id is None:
                raise RuntimeError("Failed to create portfolio balance")
            return balance_id

    @staticmethod
    def get_history(portfolio_id: int, limit: int = 30) -> List[Dict[str, Any]]:
        """Get balance history for a portfolio."""
        with get_db_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM portfolio_balance
                   WHERE portfolio_id = ?
                   ORDER BY balance_date DESC
                   LIMIT ?""",
                (portfolio_id, limit)
            ).fetchall()
            return [dict_from_row(row) for row in rows]


# Journal operations
class JournalDB:
    @staticmethod
    def create(entry_date: date, content: str, stock_id: Optional[int] = None,
               portfolio_id: Optional[int] = None,
               transaction_id: Optional[int] = None) -> int:
        """Create a journal entry."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO journal_entry (entry_date, content, stock_id,
                   portfolio_id, transaction_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (entry_date, content, stock_id, portfolio_id, transaction_id)
            )
            conn.commit()
            entry_id = cursor.lastrowid
            if entry_id is None:
                raise RuntimeError("Failed to create journal entry")
            return entry_id

    @staticmethod
    def get_recent_entries(limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent journal entries."""
        with get_db_connection() as conn:
            rows = conn.execute(
                """SELECT j.*, s.symbol, p.name as portfolio_name
                   FROM journal_entry j
                   LEFT JOIN stock s ON j.stock_id = s.id
                   LEFT JOIN portfolio p ON j.portfolio_id = p.id
                   ORDER BY j.entry_date DESC, j.created_at DESC
                   LIMIT ?""",
                (limit,)
            ).fetchall()
            return [dict_from_row(row) for row in rows]


# Initialize database on module import
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully")
