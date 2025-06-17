"""
Comprehensive test suite for Unit of Work interface in shared kernel.

Tests the foundational Unit of Work pattern as a reusable component 
across all bounded contexts. This follows TDD approach by defining 
all expected behavior before implementation.
"""

import pytest
from abc import ABC
from shared_kernel.interfaces.unit_of_work import IUnitOfWork


class TestUnitOfWorkInterface:
    """Test IUnitOfWork interface contract."""
    
    def test_unit_of_work_is_abstract_base_class(self):
        """Should be an abstract base class."""
        assert issubclass(IUnitOfWork, ABC)
        
        # Should not be instantiatable directly
        with pytest.raises(TypeError):
            IUnitOfWork()
    
    def test_unit_of_work_context_manager_methods(self):
        """Should define context manager protocol."""
        # Check that abstract methods exist
        assert hasattr(IUnitOfWork, '__enter__')
        assert hasattr(IUnitOfWork, '__exit__')
        
        # These should be abstract methods
        assert getattr(IUnitOfWork.__enter__, '__isabstractmethod__', False)
        assert getattr(IUnitOfWork.__exit__, '__isabstractmethod__', False)
    
    def test_unit_of_work_transaction_methods(self):
        """Should define transaction management methods."""
        # Check that abstract methods exist
        assert hasattr(IUnitOfWork, 'commit')
        assert hasattr(IUnitOfWork, 'rollback')
        
        # These should be abstract methods
        assert getattr(IUnitOfWork.commit, '__isabstractmethod__', False)
        assert getattr(IUnitOfWork.rollback, '__isabstractmethod__', False)


class TestUnitOfWorkImplementation:
    """Test concrete Unit of Work implementation contract."""
    
    def test_concrete_implementation_context_manager(self):
        """Should work as context manager when properly implemented."""
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self):
                self.committed = False
                self.rolled_back = False
                self.entered = False
                self.exited = False
                self.exception_occurred = False
            
            def __enter__(self):
                self.entered = True
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.exited = True
                if exc_type is not None:
                    self.exception_occurred = True
                    self.rollback()
                else:
                    self.commit()
                return False  # Don't suppress exceptions
            
            def commit(self):
                self.committed = True
            
            def rollback(self):
                self.rolled_back = True
        
        # Test successful transaction
        uow = TestUnitOfWork()
        with uow:
            pass
        
        assert uow.entered
        assert uow.exited
        assert uow.committed
        assert not uow.rolled_back
        assert not uow.exception_occurred
    
    def test_concrete_implementation_exception_handling(self):
        """Should handle exceptions properly with rollback."""
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self):
                self.committed = False
                self.rolled_back = False
                self.exception_occurred = False
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.exception_occurred = True
                    self.rollback()
                else:
                    self.commit()
                return False
            
            def commit(self):
                self.committed = True
            
            def rollback(self):
                self.rolled_back = True
        
        # Test exception handling
        uow = TestUnitOfWork()
        with pytest.raises(ValueError):
            with uow:
                raise ValueError("Test exception")
        
        assert not uow.committed
        assert uow.rolled_back
        assert uow.exception_occurred
    
    def test_manual_transaction_control(self):
        """Should support manual transaction control outside context manager."""
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self):
                self.committed = False
                self.rolled_back = False
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.rollback()
                else:
                    self.commit()
                return False
            
            def commit(self):
                if self.rolled_back:
                    raise RuntimeError("Cannot commit after rollback")
                self.committed = True
            
            def rollback(self):
                if self.committed:
                    raise RuntimeError("Cannot rollback after commit")
                self.rolled_back = True
        
        # Test manual commit
        uow = TestUnitOfWork()
        uow.commit()
        assert uow.committed
        assert not uow.rolled_back
        
        # Test manual rollback
        uow2 = TestUnitOfWork()
        uow2.rollback()
        assert not uow2.committed
        assert uow2.rolled_back


class TestUnitOfWorkPatterns:
    """Test common Unit of Work usage patterns."""
    
    def test_nested_unit_of_work_support(self):
        """Should support nested unit of work scenarios."""
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self, name: str):
                self.name = name
                self.committed = False
                self.rolled_back = False
                self.operations = []
            
            def __enter__(self):
                self.operations.append(f"{self.name}: entered")
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.operations.append(f"{self.name}: exception occurred")
                    self.rollback()
                else:
                    self.operations.append(f"{self.name}: success")
                    self.commit()
                return False
            
            def commit(self):
                self.committed = True
                self.operations.append(f"{self.name}: committed")
            
            def rollback(self):
                self.rolled_back = True
                self.operations.append(f"{self.name}: rolled back")
        
        outer_uow = TestUnitOfWork("outer")
        inner_uow = TestUnitOfWork("inner")
        
        # Test nested successful transactions
        with outer_uow:
            with inner_uow:
                pass
        
        assert outer_uow.committed
        assert inner_uow.committed
        assert "outer: entered" in outer_uow.operations
        assert "inner: entered" in inner_uow.operations
    
    def test_unit_of_work_with_repositories(self):
        """Should coordinate with repository pattern."""
        
        class MockRepository:
            def __init__(self, uow):
                self.uow = uow
                self.operations = []
            
            def add(self, entity):
                self.operations.append(f"add: {entity}")
            
            def update(self, entity):
                self.operations.append(f"update: {entity}")
            
            def delete(self, entity):
                self.operations.append(f"delete: {entity}")
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self):
                self.committed = False
                self.rolled_back = False
                self.repositories = {}
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.rollback()
                else:
                    self.commit()
                return False
            
            def commit(self):
                # Simulate persisting all repository changes
                for repo in self.repositories.values():
                    for operation in repo.operations:
                        # Simulate database persistence
                        pass
                self.committed = True
            
            def rollback(self):
                # Simulate rolling back all repository changes
                for repo in self.repositories.values():
                    repo.operations.clear()
                self.rolled_back = True
            
            def get_repository(self, repo_type):
                if repo_type not in self.repositories:
                    self.repositories[repo_type] = MockRepository(self)
                return self.repositories[repo_type]
        
        # Test coordinated repository operations
        with TestUnitOfWork() as uow:
            user_repo = uow.get_repository("users")
            order_repo = uow.get_repository("orders")
            
            user_repo.add("user-1")
            order_repo.add("order-1")
            user_repo.update("user-1")
        
        assert uow.committed
        assert len(user_repo.operations) == 2
        assert len(order_repo.operations) == 1
    
    def test_unit_of_work_isolation_levels(self):
        """Should support different transaction isolation levels."""
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self, isolation_level="READ_COMMITTED"):
                self.isolation_level = isolation_level
                self.committed = False
                self.rolled_back = False
                self.changes_visible = False
            
            def __enter__(self):
                # Simulate setting isolation level
                if self.isolation_level == "READ_UNCOMMITTED":
                    self.changes_visible = True
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.rollback()
                else:
                    self.commit()
                return False
            
            def commit(self):
                self.committed = True
                self.changes_visible = True
            
            def rollback(self):
                self.rolled_back = True
                self.changes_visible = False
        
        # Test different isolation levels
        read_uncommitted = TestUnitOfWork("READ_UNCOMMITTED")
        read_committed = TestUnitOfWork("READ_COMMITTED")
        
        with read_uncommitted:
            assert read_uncommitted.changes_visible  # Changes visible immediately
        
        with read_committed:
            assert not read_committed.changes_visible  # Changes visible only after commit
        
        assert read_committed.changes_visible  # Now visible after commit


class TestUnitOfWorkErrorScenarios:
    """Test Unit of Work error handling and edge cases."""
    
    def test_commit_failure_handling(self):
        """Should handle commit failures appropriately."""
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self, commit_should_fail=False):
                self.commit_should_fail = commit_should_fail
                self.committed = False
                self.rolled_back = False
                self.commit_attempted = False
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.rollback()
                else:
                    try:
                        self.commit()
                    except Exception:
                        self.rollback()
                        raise
                return False
            
            def commit(self):
                self.commit_attempted = True
                if self.commit_should_fail:
                    raise RuntimeError("Commit failed")
                self.committed = True
            
            def rollback(self):
                self.rolled_back = True
        
        # Test commit failure
        uow = TestUnitOfWork(commit_should_fail=True)
        with pytest.raises(RuntimeError, match="Commit failed"):
            with uow:
                pass
        
        assert uow.commit_attempted
        assert not uow.committed
        assert uow.rolled_back
    
    def test_rollback_failure_handling(self):
        """Should handle rollback failures appropriately."""
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self, rollback_should_fail=False):
                self.rollback_should_fail = rollback_should_fail
                self.committed = False
                self.rolled_back = False
                self.rollback_attempted = False
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    try:
                        self.rollback()
                    except Exception as rollback_error:
                        # Log rollback failure but don't suppress original exception
                        print(f"Rollback failed: {rollback_error}")
                else:
                    self.commit()
                return False
            
            def commit(self):
                self.committed = True
            
            def rollback(self):
                self.rollback_attempted = True
                if self.rollback_should_fail:
                    raise RuntimeError("Rollback failed")
                self.rolled_back = True
        
        # Test rollback failure (original exception should still propagate)
        uow = TestUnitOfWork(rollback_should_fail=True)
        with pytest.raises(ValueError):  # Original exception
            with uow:
                raise ValueError("Original error")
        
        assert uow.rollback_attempted
        assert not uow.rolled_back
        assert not uow.committed
    
    def test_double_commit_protection(self):
        """Should protect against double commit."""
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self):
                self.committed = False
                self.rolled_back = False
                self.commit_count = 0
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.rollback()
                else:
                    self.commit()
                return False
            
            def commit(self):
                if self.committed:
                    raise RuntimeError("Transaction already committed")
                if self.rolled_back:
                    raise RuntimeError("Cannot commit after rollback")
                self.committed = True
                self.commit_count += 1
            
            def rollback(self):
                if self.rolled_back:
                    raise RuntimeError("Transaction already rolled back")
                if self.committed:
                    raise RuntimeError("Cannot rollback after commit")
                self.rolled_back = True
        
        uow = TestUnitOfWork()
        
        # First commit should succeed
        uow.commit()
        assert uow.committed
        assert uow.commit_count == 1
        
        # Second commit should fail
        with pytest.raises(RuntimeError, match="already committed"):
            uow.commit()
        
        assert uow.commit_count == 1  # Should not increment
    
    def test_timeout_handling(self):
        """Should handle transaction timeouts."""
        
        import time
        from datetime import datetime, timedelta
        
        class TestUnitOfWork(IUnitOfWork):
            def __init__(self, timeout_seconds=1):
                self.timeout_seconds = timeout_seconds
                self.start_time = None
                self.committed = False
                self.rolled_back = False
                self.timed_out = False
            
            def __enter__(self):
                self.start_time = datetime.now()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                elapsed = datetime.now() - self.start_time
                if elapsed.total_seconds() > self.timeout_seconds:
                    self.timed_out = True
                    self.rollback()
                    if exc_type is None:
                        raise TimeoutError("Transaction timed out")
                elif exc_type is not None:
                    self.rollback()
                else:
                    self.commit()
                return False
            
            def commit(self):
                if self.timed_out:
                    raise RuntimeError("Cannot commit timed out transaction")
                self.committed = True
            
            def rollback(self):
                self.rolled_back = True
        
        # Test timeout scenario
        uow = TestUnitOfWork(timeout_seconds=0.1)
        with pytest.raises(TimeoutError, match="timed out"):
            with uow:
                time.sleep(0.2)  # Exceed timeout
        
        assert uow.timed_out
        assert uow.rolled_back
        assert not uow.committed