"""
Tests for database connection abstraction.

Following TDD approach - these tests define the expected behavior
of the database connection management.
"""

import pytest
import tempfile
import os
import sqlite3
from pathlib import Path
from infrastructure.persistence.database_connection import DatabaseConnection


class TestDatabaseConnection:
    """Test suite for DatabaseConnection."""
    
    def setup_method(self):
        """Set up test database file."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
    
    def teardown_method(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_connection_initialization(self):
        """Should initialize database connection with file path."""
        # Act
        db_conn = DatabaseConnection(self.temp_db.name)
        
        # Assert
        assert db_conn.database_path == self.temp_db.name
        assert isinstance(db_conn.database_path, str)
    
    def test_database_connection_with_pathlib_path(self):
        """Should accept pathlib.Path objects."""
        # Arrange
        path_obj = Path(self.temp_db.name)
        
        # Act
        db_conn = DatabaseConnection(path_obj)
        
        # Assert
        assert str(db_conn.database_path) == str(path_obj)
    
    def test_initialize_schema_creates_tables(self):
        """Should initialize database schema with all required tables."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        
        # Act
        db_conn.initialize_schema()
        
        # Assert - verify tables exist
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            
            # Check if stock table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='stock'
            """)
            assert cursor.fetchone() is not None
            
            # Verify stock table structure
            cursor.execute("PRAGMA table_info(stock)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            expected_columns = ['id', 'symbol', 'name', 'industry_group', 'grade', 'notes']
            for col in expected_columns:
                assert col in column_names
    
    def test_initialize_schema_idempotent(self):
        """Should be safe to call initialize_schema multiple times."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        
        # Act
        db_conn.initialize_schema()
        db_conn.initialize_schema()  # Second call should not error
        
        # Assert - tables should still exist and be functional
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stock")
            result = cursor.fetchone()
            assert result[0] == 0  # Empty table
    
    def test_get_connection_returns_sqlite_connection(self):
        """Should return SQLite connection object."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        db_conn.initialize_schema()
        
        # Act
        connection = db_conn.get_connection()
        
        # Assert
        assert isinstance(connection, sqlite3.Connection)
        
        # Verify connection works
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM stock")
        result = cursor.fetchone()
        assert result[0] == 0
        
        connection.close()
    
    def test_get_connection_enables_foreign_keys(self):
        """Should enable foreign key constraints."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        db_conn.initialize_schema()
        
        # Act
        connection = db_conn.get_connection()
        
        # Assert
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1  # Foreign keys enabled
        
        connection.close()
    
    def test_get_connection_sets_row_factory(self):
        """Should set row factory for column access by name."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        db_conn.initialize_schema()
        
        # Act
        connection = db_conn.get_connection()
        
        # Assert
        assert connection.row_factory == sqlite3.Row
        
        # Test row factory works
        cursor = connection.cursor()
        cursor.execute("INSERT INTO stock (symbol, name) VALUES (?, ?)", ("TEST", "Test Inc."))
        connection.commit()
        
        cursor.execute("SELECT symbol, name FROM stock WHERE symbol = ?", ("TEST",))
        row = cursor.fetchone()
        
        # Should be able to access by column name
        assert row["symbol"] == "TEST"
        assert row["name"] == "Test Inc."
        
        connection.close()
    
    def test_context_manager_support(self):
        """Should support context manager protocol."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        db_conn.initialize_schema()
        
        # Act & Assert
        with db_conn.get_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
            
            # Use the connection
            cursor = conn.cursor()
            cursor.execute("INSERT INTO stock (symbol, name) VALUES (?, ?)", ("CTX", "Context Inc."))
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM stock")
            result = cursor.fetchone()
            assert result[0] == 1
        
        # Connection should be closed automatically
    
    def test_transaction_support(self):
        """Should support database transactions."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        db_conn.initialize_schema()
        
        # Act - successful transaction
        with db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO stock (symbol, name) VALUES (?, ?)", ("TXN1", "Transaction 1"))
            cursor.execute("INSERT INTO stock (symbol, name) VALUES (?, ?)", ("TXN2", "Transaction 2"))
            conn.commit()
        
        # Assert - both records should exist
        with db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stock")
            result = cursor.fetchone()
            assert result[0] == 2
    
    def test_transaction_rollback_on_error(self):
        """Should rollback transaction on error."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        db_conn.initialize_schema()
        
        # Act - transaction that fails
        try:
            with db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO stock (symbol, name) VALUES (?, ?)", ("ROLL1", "Rollback 1"))
                
                # This should succeed
                conn.commit()
                
                # This should fail (duplicate symbol)
                cursor.execute("INSERT INTO stock (symbol, name) VALUES (?, ?)", ("ROLL1", "Rollback Duplicate"))
                conn.commit()
        except sqlite3.IntegrityError:
            pass  # Expected error
        
        # Assert - only first record should exist
        with db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stock WHERE symbol = ?", ("ROLL1",))
            result = cursor.fetchone()
            assert result[0] == 1  # Only one record
    
    def test_close_connection(self):
        """Should close database connection properly."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        db_conn.initialize_schema()
        
        # Act
        connection = db_conn.get_connection()
        assert connection is not None
        
        db_conn.close()
        
        # Assert - connection should be closed
        # Note: SQLite connections don't have a simple "is_closed" check,
        # so we test by trying to use it
        with pytest.raises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")
    
    def test_connection_timeout_configuration(self):
        """Should configure connection timeout."""
        # Arrange & Act
        db_conn = DatabaseConnection(self.temp_db.name, timeout=30.0)
        db_conn.initialize_schema()
        
        # Assert - connection should work with timeout
        with db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    
    def test_invalid_database_path_raises_error(self):
        """Should raise error for invalid database path."""
        # Arrange - path to non-existent directory
        invalid_path = "/nonexistent/directory/database.db"
        
        # Act & Assert
        with pytest.raises(Exception):  # Could be various exceptions depending on OS
            db_conn = DatabaseConnection(invalid_path)
            db_conn.initialize_schema()
    
    def test_database_connection_string_representation(self):
        """Should have meaningful string representation."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        
        # Act
        str_repr = str(db_conn)
        
        # Assert
        assert "DatabaseConnection" in str_repr
        assert self.temp_db.name in str_repr
    
    def test_concurrent_connections(self):
        """Should support multiple concurrent connections."""
        # Arrange
        db_conn = DatabaseConnection(self.temp_db.name)
        db_conn.initialize_schema()
        
        # Act
        conn1 = db_conn.get_connection()
        conn2 = db_conn.get_connection()
        
        # Assert - both connections should work
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        
        cursor1.execute("INSERT INTO stock (symbol, name) VALUES (?, ?)", ("CON1", "Connection 1"))
        conn1.commit()
        
        cursor2.execute("SELECT COUNT(*) FROM stock")
        result = cursor2.fetchone()
        assert result[0] == 1  # Should see committed data
        
        conn1.close()
        conn2.close()